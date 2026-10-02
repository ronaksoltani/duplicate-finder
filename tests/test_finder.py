from dupe_finder.finder import find_duplicates, fingerprint


def test_fingerprint_is_stable_and_duplicate_group_is_read_only(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "nested" / "second.txt"
    second.parent.mkdir()
    first.write_bytes(b"same content")
    second.write_bytes(b"same content")
    assert fingerprint(first) == fingerprint(second)
    groups, candidates, unreadable = find_duplicates(tmp_path)
    assert len(groups) == 1
    assert groups[0].reclaimable_bytes == len(b"same content")
    assert candidates == 2 and unreadable == 0
    assert first.exists() and second.exists()


def test_unique_files_do_not_form_duplicate_groups(tmp_path):
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.txt").write_text("bravo!", encoding="utf-8")
    groups, candidates, unreadable = find_duplicates(tmp_path)
    assert groups == []
    assert candidates == 0 and unreadable == 0
