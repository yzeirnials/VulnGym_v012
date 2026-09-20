#!/usr/bin/env python3
"""Measure fixed Git snapshots without installing or executing project code."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args, input_data=None):
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), *args],
        input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def manifest_content_sha256(rows):
    """Hash parsed membership, independent of JSON spacing and LF/CRLF transport."""
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def path_exclusion(name, policy):
    path = PurePosixPath(name)
    excluded = set(policy["excluded_directory_names"])
    if any(part.lower() in excluded for part in path.parts[:-1]):
        return "directory"
    if any(fnmatch.fnmatchcase(path.name.lower(), pattern) for pattern in policy["excluded_file_patterns"]):
        return "generated_or_minified_filename"
    return None


def source_path(row, source_root, source_map):
    key = (row["repo_url"], row["commit"])
    if key in source_map:
        return Path(source_map[key])
    if source_root is None:
        raise ValueError(f"No source path for {key}")
    url = urlparse(row["repo_url"])
    repo_key = re.sub(r"[^A-Za-z0-9]+", "__", url.netloc + url.path.rstrip("/"))
    return Path(source_root) / f"{repo_key}__{row['commit']}"


def measure(row, root, policy, cloc_command):
    root = root.resolve()
    head = git(root, "rev-parse", "HEAD").decode().strip()
    if head != row["commit"]:
        raise ValueError(f"Source HEAD does not match requested commit: {row['repo_url']} {row['commit']}")
    git(root, "diff", "--quiet", "HEAD", "--")
    tree = git(root, "rev-parse", "HEAD^{tree}").decode().strip()
    files, excluded = {}, Counter()
    for record in git(root, "ls-tree", "-r", "--long", "-z", "HEAD").split(b"\0"):
        if not record:
            continue
        meta, encoded_name = record.split(b"\t", 1)
        mode, kind, blob, size = meta.split()
        name = encoded_name.decode("utf-8")
        if mode not in (b"100644", b"100755") or kind != b"blob":
            excluded["symlink_or_submodule"] += 1
            continue
        reason = path_exclusion(name, policy)
        if reason:
            excluded[reason] += 1
            continue
        if "\n" in name or "\r" in name:
            raise ValueError("cloc list-file cannot represent a filename containing a newline")
        files[name] = int(size)

    attrs = git(root, "check-attr", "-z", "--stdin", *policy["git_attributes_excluded"],
                input_data=b"".join(name.encode() + b"\0" for name in files)).split(b"\0")
    marked = set()
    for i in range(0, len(attrs) - 2, 3):
        if attrs[i + 2] in (b"set", b"true"):
            marked.add(attrs[i].decode())
    header = re.compile(policy["generated_header_pattern"])
    for name in list(files):
        if name in marked:
            excluded["git_generated_or_vendored_attribute"] += 1
            del files[name]
            continue
        file_path = root / name
        if not file_path.is_file() or file_path.is_symlink():
            raise ValueError(f"Tracked regular file missing or replaced: {name}")
        with file_path.open("rb") as handle:
            prefix = handle.read(policy["generated_header_bytes"]).decode("utf-8", errors="replace")
        if header.search(prefix):
            excluded["generated_header"] += 1
            del files[name]

    with tempfile.TemporaryDirectory(prefix="vulngym-cloc-") as temp:
        temp = Path(temp)
        listing = temp / "files.txt"
        listing.write_text("".join(name + "\n" for name in files), encoding="utf-8")
        config = temp / "options.txt"
        config.write_text("", encoding="utf-8")
        proc = subprocess.run(
            [*cloc_command, f"--config={config}", f"--list-file={listing}", "--json",
             "--by-file", "--skip-uniqueness", "--no-autogen", "--timeout=0", "--quiet"],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True,
        )
        if proc.stderr.strip():
            raise ValueError(f"cloc diagnostics for {row['repo_url']}: {proc.stderr[:1500]}")
        measured = json.loads(proc.stdout)

    languages = defaultdict(lambda: {"code": 0, "files": 0, "bytes": 0, "blank": 0, "comment": 0})
    excluded_languages = Counter()
    recognized = set()
    for name, result in measured.items():
        if name in ("header", "SUM"):
            continue
        normalized = name.replace("\\", "/")
        if normalized.startswith("./"):
            normalized = normalized[2:]
        if normalized not in files:
            raise ValueError(f"cloc returned an unexpected file: {name}")
        recognized.add(normalized)
        language = result["language"]
        if language not in policy["included_languages"]:
            excluded_languages[language] += 1
            continue
        totals = languages[language]
        for field in ("code", "blank", "comment"):
            totals[field] += result[field]
        totals["files"] += 1
        totals["bytes"] += files[normalized]
    excluded["unrecognized_binary_empty_or_cloc_autogen"] += len(files) - len(recognized)
    git(root, "diff", "--quiet", "HEAD", "--")
    if git(root, "rev-parse", "HEAD").decode().strip() != head:
        raise ValueError("Source checkout changed during measurement")
    if not languages:
        raise ValueError(f"No counted source languages for {row['repo_url']}")
    return {
        "repo_url": row["repo_url"], "commit": head, "git_tree": tree,
        "batch_id": row["batch_id"], "entry_ids": row["entry_ids"],
        "sloc": sum(v["code"] for v in languages.values()),
        "source_files": sum(v["files"] for v in languages.values()),
        "source_bytes": sum(v["bytes"] for v in languages.values()),
        "languages": dict(sorted(languages.items())),
        "excluded_files_by_reason": dict(sorted(excluded.items())),
        "excluded_language_files": dict(sorted(excluded_languages.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/batch_manifest.jsonl")
    parser.add_argument("--policy", type=Path, default=Path(__file__).with_name("source_size_policy.json"))
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--source-map", type=Path, help="JSONL with repo_url, commit, cache_path (local only)")
    parser.add_argument("--cloc", type=Path, required=True, help="Official cloc v2.10 Perl script")
    parser.add_argument("--perl", default="perl")
    parser.add_argument("--jobs", type=int, default=2, help="Concurrent snapshots; does not affect counts")
    parser.add_argument("--output", type=Path, default=ROOT / "records/source_sizes.json")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    if hashlib.sha256(args.cloc.read_bytes()).hexdigest() != policy["cloc_sha256"]:
        raise ValueError("cloc does not match the pinned official v2.10 script")
    command = [args.perl, str(args.cloc.resolve())]
    version = subprocess.check_output([*command, "--version"], text=True).strip()
    if version != policy["cloc_version"]:
        raise ValueError(f"Expected cloc {policy['cloc_version']}, found {version}")
    manifest = read_jsonl(args.manifest)
    keys = [(r["repo_url"], r["commit"]) for r in manifest]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate snapshot in batch manifest")
    mapping = {(r["repo_url"], r["commit"]): r["cache_path"] for r in read_jsonl(args.source_map)} if args.source_map else {}
    results = []
    def process(row):
        return measure(row, source_path(row, args.source_root, mapping), policy, command)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for index, result in enumerate(pool.map(process, manifest), 1):
            results.append(result)
            print(f"{index}/{len(manifest)} {result['batch_id']} {result['repo_url']} {result['commit'][:12]} SLOC={result['sloc']}", flush=True)
    output = {"schema_version": 1, "cloc_version": version, "policy": policy,
              "manifest_content_sha256": manifest_content_sha256(manifest), "snapshots": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
