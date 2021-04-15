# Doc Store

[![flake8 linting](https://github.com/steiza/docstore/actions/workflows/run_flake8.yml/badge.svg)](https://github.com/steiza/docstore/actions/workflows/run_flake8.yml)

This project is meant for any civics-minded organization that needs a simple place to host documents publicly.

On the homepage you can see recently uploaded documents:

![Recently uploaded documents](https://raw.github.com/steiza/docstore/main/readme_images/home_page.png)

There's a search page that will search through the document metadata (but not the document contents):

![Search page](https://raw.github.com/steiza/docstore/main/readme_images/search.png)

Clicking on a document will take you to a page with document details and a download link:

![Document detail page](https://raw.github.com/steiza/docstore/main/readme_images/doc.png)

And there's a basic password protected management page to clean up details or delete documents if needed:

![Management page](https://raw.github.com/steiza/docstore/main/readme_images/edit.png)

Document metadata is stored in an on-disk sqlite database and the files themselves are stored on disk.

### Run the software

If you want to run your own version, after you check out the repository you'll need to create a basic `settings.yml` file::

```
region: 'My City'
password: '__make_your_own_management_password__'
cookie_secret: '__this_can_be_anything_it_is_just_for_the_server__'
google_analytics_id: '__optional_just_remove_this_line_if_not_needed__'
max_file_size: '__optional_maximum_upload_size_allowed__'
```

Then run the server:

```
./docstore
```

Note that this project uses HTTP Basic auth - if you host this project without HTTPS the management password will be sent over the network in the clear. Ideally, run this server behind a reverse proxy like nginx which performs TLS termination for you.

### Installing dependencies

Using pipenv:

```
pipenv install -r requirements.txt
```
