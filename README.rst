Doc Store
=========

This project is meant for any civics-minded organization that needs a simple place to host documents publicly.

On the homepage you can see recently uploaded documents:

.. image:: https://raw.github.com/steiza/docstore/master/readme_images/home_page.png

There's a search page that will search through the document metadata (but not the document contents):

.. image:: https://raw.github.com/steiza/docstore/master/readme_images/search.png

Clicking on a document will take you to a page with document details and a download link:

.. image:: https://raw.github.com/steiza/docstore/master/readme_images/doc.png

And there's a basic password protected management page to clean up details or delete documents if needed:

.. image:: https://raw.github.com/steiza/docstore/master/readme_images/edit.png

Document metadata is stored in an on-disk sqlite database and the files themselves are stored on disk.

If you want to run your own version, after you check out the repository you'll need to create a basic `settings.yml` file::

    region: 'Ann Arbor Area'
    password: '__make_your_own_management_password__'
    cookie_secret: '__this_can_be_anything_it_is_just_for_the_server__'

Note that this project uses HTTP Basic auth - if you host this project without HTTPS the management password will be sent over the network in the clear.
