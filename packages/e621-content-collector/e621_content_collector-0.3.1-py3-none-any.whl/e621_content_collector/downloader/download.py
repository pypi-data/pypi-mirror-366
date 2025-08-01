import json
import os

import requests
import typer
from requests import Response

# Declare and initialize a set representing the tag sets that the tool should
# download content with.
tag_sets: set = {}

# Declare and initialize a set representing the tags that the tool should
# ignore/skip when downloading posts from e621.
blacklisted_tags: set = {}

def read_tag_file(tag_file_name: str, sort_tags: bool = False, create_file_if_missing: bool = True) -> set:
    """Reads a provided "tag file" (e.g., tag_sets.txt, blacklisted_tags.txt)
    into a set, cleans the set's contents, and returns the set for use by the
    tool.

    ## Arguments
    - `tag_file_name`: A string representing the name of the tag file to read
    and process (e.g., `tag_sets.txt`, `blacklisted_tags.txt`).
    - `sort_tags`: A boolean indicating whether the set of tags read from the
    provided tag file should be sorted before being returned by the function.
    Defaults to False since sorting is more of a "nice to have" and can have
    performance implications if done against a significantly large set of tags.
    - `create_file_if_missing`: A boolean indicating whether the referenced tag
    file should be created if it does not exist. Defaults to True since some
    tag files are necessary for the tool to run as expected.
    
    ## Notes
    - This function is intentionally generic, as the logic used to read and
    prepare the contents of tag_sets.txt and blacklisted_tags.txt is
    near-identical (and thus shouldn't be implemented twice)."""
    # Declare and initialize an empty set which will be used to represent the
    # tags in the provided tag file (if the file exists and includes any tags).
    tags: set = {}

    # Try to open the tag file, read its contents in as a set, clean the values
    # read into the set, and (optionally) sort the set to prepare it for use by
    # the core downloader logic. Optionally, if the referenced tag file does
    # not exist, create it.
    try:
        with open(tag_file_name, 'r') as tag_file:
            # Read the tag file's contents in as a set.
            tags = set(tag_file.readlines())

            # Clean the values in the tags set by removing newlines. This will
            # make it easier to use these values in the core downloader logic.
            for tag in tags:
                # Remove the raw value from the set.
                tags.remove(tag)

                # Replace any escaped newlines with the empty string.
                tag = tag.replace('\n', '')

                # Added the cleaned version of the tag back to tags for
                # further processing.
                tags.add(tag)

            # If desired, sort the tags in the set.
            if sort_tags:
                tags = sorted(tags)
    except FileNotFoundError:
        with open(tag_file_name, 'w') as tag_file:
            tag_file.write('')

    return tags

def read_tag_sets_file() -> set:
    """Reads the provided tag_sets.txt file to gain a reference for the tag
    sets to download against and returns it for use by other parts of the tool.

    ## Notes
    - A potential enhancement being considered is to provide the user an option
    to specify a custom tag sets file (rather than using the default
    tag_sets.txt file that the tool provides). However, this option is not
    currently available.
    - Another potential enhancement being considered is to provide the user an
    option to *not* sort the tag set list. The sorting behavior included in the
    logic at present is included more as a convenience (it can provide users a
    reference for how far in their tag set list the tool is when running), but
    isn't necessary for the tool to run. In addition, the sorting behavior
    could create performance issues when reading in tag set lists for extremely
    large lists (though this is likely more of an edge case than something that
    the typical user would experience).
    """
    return read_tag_file(tag_file_name='tag_sets.txt', sort_tags=True, create_file_if_missing=True)

def read_blacklisted_tags_file() -> set:
    """Reads the provided blacklisted_tags.txt file to gain a reference for
    tags that the user does not want included in content downloaded by the
    tool. Tags referenced in this file (and the resulting set) will cause the
    tool to skip the download step for any posts which are tagged with one or
    more blacklisted tags.

    ## Notes
    - A potential enhancement being considered is to provide the user an option
    to specify a custom blacklist file (rather than using the default
    blacklisted_tags.txt file that the tool provides). However, this option is
    not currently available.
    """
    return read_tag_file(tag_file_name='blacklisted_tags.txt', sort_tags=False, create_file_if_missing=True)
        
def download_posts(tag_set: str, blacklisted_tags: set = {}) -> None:
    """Downloads posts associated with a provided tag set.

    ## Arguments
    - `tag_set`: A string representing the set of tags to use to search for
    posts. The format of this string matches what a user would enter if
    searching for posts directly on e621.
    - `blacklisted_tags`: A set representing the set of tags which the user has
    specified as "blacklisted" tags. Similar to how the blacklisting feature on
    the e621 website works, content including one or more blacklisted tags will
    not be provided to the user. In this implementation, the tool will simply
    skip the download step for any posts including blacklisted tags.

    ## Notes
    - A potential enhancement being considered is to provide the user an option
    to download posts without specifying any tags, which would effectively
    download the latest posts on e621, regardless of how they're tagged.
    - Another potential enhancement being considered is to provide the user an
    option to specify a custom download location (where downloaded posts are
    stored on the local machine).
    """
    # Check whether a "downloads" folder exists in the current working
    # directory and create it if it doesn't. This directory needs to be present
    # before downloading post data to avoid an error being thrown while
    # downloading(in the event that the directory doesn't exist).
    if not os.path.exists(os.path.join(os.getcwd(), 'downloads')):
        os.mkdir('downloads')

    # Replace spaces in the tag set with the URL encoded version of the space
    # character. While this isn't necessarily necessary, it makes requests to
    # the e621 API more proper.
    tag_set_string: str = tag_set.replace(' ', '%20')

    # Declare and initialize variable to track which page of posts the
    # downloader is requesting content from and whether there are more posts to
    # process. These are necessary because the e621 API returns content data in
    # pages rather than all at once, and does not indicate whether there is a
    # "next" page.
    page_number: int = 1
    more_posts_available: bool = True

    # Decare and initialize a dictionary of headers to include with the content
    # request to e621. This *should* just be the user agent that identifies the
    # tool to e621 (per e621's requirement for user agent information for API
    # requests).
    headers: dict = {'User-Agent': 'darkroastcreative/e621-content-collector'}

    # Process the request, paging through the set of available posts until
    # either the page limit is reached or the tool detects that there are no
    # more posts available for the specified tag set.
    while page_number < 751 and more_posts_available:
        # Submit a request to the e621 API for posts matching the provided tag set and page number.
        response: Response = requests.get(url=f'https://e621.net/posts.json?tags={tag_set_string}&page={page_number}', headers=headers)

        # Process the response from the e621 API.
        if response.status_code == 200:
            # Parse the response JSON from the e621 API to a Python object for
            # processing. This line grabs justs the content of the "posts" property
            # of the response because that's the part needed to parse and download
            # the posts referenced in the response.
            posts = json.loads(response.content)['posts']

            if len(posts) > 0:
                more_posts_available = True
            else:
                more_posts_available = False

            # Iterate over the set of posts, extracting post metadata (ID, URL, tag
            # information) and downloading each post.
            for post in posts:
                # Extract post ID. This will be used to name the downloaded file.
                id: int = post['id']

                # Extract the URL for the source content (image, video, animation,
                # etc.). The content at this URL will be the content downloaded to
                # represent the post.
                url: str = post['file']['url']

                # Extract tag information into a flattened/unified list of post
                # tags. This list will be used to identify posts including
                # blacklisted tags (if any are specified by the user) so posts
                # matching this criteria aren't downloaded by the tool.
                tags: list = []
                tags.extend(post['tags']['general'])
                tags.extend(post['tags']['artist'])
                tags.extend(post['tags']['contributor'])
                tags.extend(post['tags']['copyright'])
                tags.extend(post['tags']['character'])
                tags.extend(post['tags']['species'])
                tags.extend(post['tags']['meta'])
                tags.extend(post['tags']['lore'])

                # Check whether the post includes any blacklisted tags and
                # whether the URL value for the post is non-null. If the post
                # includes no blacklisted tags and has a URL value, proceed to
                # download it. The condition related to null URL values is
                # present to account for an oddity with the e621 API in which
                # some posts are included in API responses without URL values.
                if len(set(tags) & set(blacklisted_tags)) == 0 and url is not None:
                    # Get the file extension for the post. This will be used to
                    # determine which file extension to use when downloading/saving
                    # the post content locally.
                    file_extension: str = url.split('.')[-1]

                    # Get the post data. This will be written to the local machine.
                    post_data: bytes = requests.get(url).content

                    # Write the post file to the local machine.
                    with open(os.path.join(os.getcwd(), 'downloads', f'{id}.{file_extension}'), 'wb') as post_file:
                        post_file.write(post_data)

            # Increment the page number variable so the tool can proceed to
            # check for the next page of posts.
            page_number += 1

def run_download() -> None:
    """Reads in the contents of tag_sets.txt and proceeds to download posts
    matching each provided tag set.

    ## Notes
    - Options will likely be added to this method at a later time to allow the
    user more control over download behavior.
    """
    # Read the set of tag sets to download against from tag_sets.txt.
    tag_sets = read_tag_sets_file()

    # Read the set of blacklisted tags to skip when downloading content from
    # e621.
    blacklisted_tags = read_blacklisted_tags_file()

    # For each tag set, download the posts matching the tag set.
    for tag_set in tag_sets:
        download_posts(tag_set=tag_set, blacklisted_tags=blacklisted_tags)