============================
BTC Version Control Manager
============================

This is a Django app that add functionality to track model object
versions for any other Django application

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "version_control" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'version_control',
      )

2. Add "version_control" middleware to middleware list in project settings::

      MIDDLEWARE = [
          ...
          'version_control.middleware.VersionControlMiddleware',
      ]

3. Include the "version_control" URLconf in your project urls.py like this::

      path('version_control/', include('version_control.urls')),

4. Setup project cache handler (Redis or another one).

5. Register and setup "version_control" models in Django admin for use in project.

6. Add class "AbstractVersionControl" to every model that must be tracked.
