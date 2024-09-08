# The Auth Microservice

### Description

This microservice is responsible for handling user authentication using DRF token auth.

### Routing

> main route = **auth**

##### Register:
    > Description: This route is responsible for user registration. User profile also get created in the process.
    > url = /register
    > method = post
    > data = username, email, password
    > return = auth token if no error occurs

##### Login:
    > Description: This route is responsible for user login
    > url  = /login
    > method = post
    > data = username, password
    > return = auth token if no error occurs

###### Profile:
    > Description: This route is responsible for all CRUD operations on user profile
    > url = ""
    > method: 
        > get: to retrieve user profile
        > put: to update user profile
        > delete: to delete user

###### Update Password:
    > Description: This route is responsible for updating password
    > method: put
    > url: /update-password
    > data:
        > old_password
        > new_password
    > return: update successful unless there is an error

###### Update Email:
    > Description: This route is responsible for updating email
    > method: put
    > url: /update-email
    > data:
        > email
    > return: update successful unless there is an error

###### Update Username:
    > Description: This route is responsible for updating username
    > method: put
    > url: /update-username
    > data:
        > username
    > return: update successful unless there is an error

######  Validate Auth:
    > Description: This route is responsible for validating the authenticated user
    > method: get
    > url: /validate-auth
    > return: True if validation successful and vice versa


###### Upload Avatar:
    > Description: This route is responsible for updating and uploading of user avatar
    > method: post
    > url: /upload-avatar
    > data:
        > media
    > return: update successful unless there is an error