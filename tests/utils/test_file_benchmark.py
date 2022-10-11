from ddb.utils.file import FileWalker


def file_walker_real_project():
    fw = FileWalker(
        [],
        ["**/.git",
         "**/.idea",
         "**/node_modules",
         "**/vendor",
         "**/target",
         "**/dist"],
        [],
        [],
        [],
        "/home/toilal/projects/carbon-saver/platform.carbon-saver")

    return list(fw.items)


def xtest_should_bench(benchmark):
    result = benchmark(file_walker_real_project)
    assert len(result) == 15144
