## Downloader Web App

### Purpose
Prior to this application, OpenAPS staff relied on manual and time-intensive processes to extract and distribute the data held within the OpenAPS Data Commons to researchers. The purpose of this application therefore was to replace the manual elements of this process with an automated solution, which would reduce the input required from OpenAPS staff, and provide researchers with faster and more comprehensive access to data from the OpenAPS data commons. Additionally, this application hosts dashboards which researchers can use to gain light analytical insights regarding data from the OpenAPS Data Commons.

### Elements

-   **Download page**: This page contains a form that researchers can use to download data sourced from the Data Commons. This form includes options which allow researchers to specify the filetype and records they wish to source, and filter by date-range.

<p align="center">
  <img src="https://github.com/Mudano/open-aps-streaming/blob/downloader-app/data-management-app/downloader/static/images/git_images/downloader.JPG" width="60%">
</p>

-   **Analytics Page**: This page contains a series of dashboards which provide key insights surrounding data sourced from the OpenAPS Data Commons, including metrics such as the amount of users who have donated data, and average trends in blood-glucose levels.

<p align="center">
  <img src="https://github.com/Mudano/open-aps-streaming/blob/downloader-app/data-management-app/downloader/static/images/git_images/analytics.JPG" width="60%">
</p>


### Setup
#### Deployment


#### Dependencies/Requirements



#### Parameters




#### Security

##### Registration
Excluding the admin account which is created during the applications initialisation, all other accounts are added via the following process.

1. A user applies for access to the site via  the 'Register' link on the login page

2. An admin receives a message outlining the users application, and can then proceed to approve/reject this application using the 'Applications' button on the admin page

3. Upon accepting the application, the applicant will receive an email containing a link to the site's verification page, as well as a verification code

4. After entering the verification code and assigning a password, a user will be able to login and access the rest of the sites content

**Nb**: *An admin can also add a user directly, by entering their email in the 'Add User' link on the admin page. This essentially cuts out the first two steps of the above process.*

##### Credentials

