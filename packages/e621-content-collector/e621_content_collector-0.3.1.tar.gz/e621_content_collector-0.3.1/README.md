# e621 Content Collector

A simple tool for gathering content from [e621](https://e621.net) for local use. Specify the tags that you'd like to target, run the tool, and let it fetch that content for your enjoyment.

This project is a spiritual successor to [FiddyFive/e621-batch-downloader](https://github.com/FiddyFive/e621-batch-downloader), created in response to the original project's owner being unresponsive to pull requests and issues. This project is not a fork of `FiddyFive/e621-batch-downloader` nor does it use any of its source code, but it does offer similar features for users looking to use a tool that is actively maintained.

## ⚠️ WARNING

The first version of this tool is actively being developed from scratch, and as such should be considered in its "alpha" stages. Expect that the tool, its source code, and its functionality will be incomplete and buggy at this point in time.

## Features

- Download e621 content based on user-specified tag sets (tag combinations, exactly like what you would enter when searching e621 natively).
- Blacklist tags representing content that you never want to see included in content downloaded by the tool.
- Use tool as a standalone CLI (i.e., without requiring the user to run from source or within tools like VS Code).

### In Development

- Track content you've already downloaded and skip it if it comes up in a new download operation.

### Queued for Development

- Add user guide.
- Add exception handling logic.
- Log what the tool does during each run.

### Ideas for a Future Release

- Add CI/CD pipeline.
- Limit download activity to a certain number of posts.
- Limit download activity to a certain number of pages.
- "Smart incremental downloads" (effectively, handle downloads for tag sets that you repeatedly search for in the tool in a more efficient way).
- Provide option for a user interface (ideal for those who prefer a more visually-oriented tool over a CLI).

## Privacy Notice

This tool will not collect user data or include telemetry features to indicate what you do with it or how it's running. As such, the development team will not know if users are encountering unexpected errors unless they are reported, nor will we know how users are using the tool. If you would like to provide feedback, please feel free to [open a new issue on GitHub](https://github.com/darkroastcreative/e621-content-collector/issues/new/choose) or reach out to the maintainers privately.

Should the privacy practices of the tool ever change, this notice will change at the same time. However, there are no plans to incorporate telemetry or activity tracking features into the tool.
