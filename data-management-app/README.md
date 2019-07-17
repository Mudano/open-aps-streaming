## Downloader Web App

### Purpose
Prior to this application, OpenAPS staff relied on manual processes to extract and distribute the data held within the OpenAPS Data Commons to researchers. The purpose of this application therefore was to provide a portal which could automate this process, with the intention of reducing waste and improving accessibility for researchers.

### Pages

-   **Download page**: This page contains a form that researchers can use to download data sourced from the Data Commons. This form includes options which allow researchers to specify the filetype and records they wish to source, and filter by date-range.

<p align="center">
  <img src="https://github.com/Mudano/open-aps-streaming/blob/downloader-app/data-management-app/downloader/static/images/git_images/downloader.JPG" width="60%">
</p>

-   **Analytics Page**: Through a series of dashboards, this page provides information relating to the demographics and metadata of our donatees, and also an analytical breakdown of key metrics related to our donatees **APS** data, such as trends in blood-glocose level throughout the day.

<p align="center">
  <img src="https://github.com/Mudano/open-aps-streaming/blob/downloader-app/data-management-app/downloader/static/images/git_images/analytics.JPG" width="60%">
</p>


### Setup
#### Deployment


#### Dependencies/Requirements

The application is ran with **Python 3.6**, with the <a href="https://github.com/Mudano/open-aps-streaming/blob/master/data-management-app/setup/requirements.txt">requirements.txt</a> file in the setup folder specifying all the required Python packages and versions. The application is based on a PostgreSQL database and uses SQLAlchemy as an interaction layer.

The dependencies required for the frontend of the application are specified in the `<head>` tag of the apps <a href="">layout.html</a> template.




#### Security

##### Authentication Parameters

The passwords and tokens required to run the app are sourced from the following environment variables:

- **DOWNLOADER_SECRET_KEY** - The secret key which is used when initialising the app
- **POSTGRES_ (USER, PASSWORD, HOST, PORT, DB)** - Credentials for connecting to the database
- **DOWNLOADER_APP_EMAIL** - The email address used by the app for messaging users/admins
- **DOWNLOADER_EMAIL_PASSWORD** - The password for above email
- **DOWNLOADER_PUBLIC_URL** - The public URL used by the app
- **DOWNLOADER_ADMIN_EMAIL** - The email to notify when a new user registers
- **METABASE_SECRET_KEY** - The secret key used for embedding our Metabase dashboards
- **METABASE_URL** - The URL of a hosted metabase instance
- **DOWNLOADER_SLACK_KEY** - A Slack App API key used for sending error notifications to Slack

##### Registration
Excluding the admin account which is created during the applications initialisation, all other accounts are added via the following process.

1. A user applies for access to the site via  the 'Register' link on the login page

2. An admin receives a message outlining the users application, and can then proceed to approve/reject this application using the 'Applications' button on the admin page

3. Upon accepting the application, the applicant will receive an email containing a link to the site's verification page, as well as a verification code

4. After entering the verification code and assigning a password, a user will be able to login and access the rest of the sites content

**Nb**: *An admin can also add a user directly, by entering their email in the 'Add User' link on the admin page. This essentially cuts out the first two steps of the above process.*

##### Credentials

