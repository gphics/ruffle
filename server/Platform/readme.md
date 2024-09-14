# Platform Microservice

### Description
A microservice responsible for the CRUD operations on the Channel and Publisher model



#### Local Port = 4040

### Models:
    > Channel
    > Publisher

#### Rules:
    > A user can only create one channel
    > Once a user create a channel, an admin publisher profile is created
    > Only channel admin is can perform CRUD operations for the channel publisher
    > But a publisher have the permission to leave a channel
    > A user can only be a publisher in one channel
    > A channel can only have at most 4 publishers including it's owner making 5

### Routes
> Base route = ""

### Routing 

##### Channel:
    > Description: This route is responsible for CRUD operations on the channel model.
    > url = /channel
    > method:
        > post : for creating the channel
        > put : for updating the channel
        > get : for retrieving the channel whose public_id was provided as a url param
        > delete : for deleting the channel whose public_id was provided as a url param 
    > data :
        > name
        > description
    > return = return a success message if no error
    > Note:
        > The authenticated user will be used as the owner of the channel


##### Publisher:
    > Description: This route is responsible for CRUD operations on the publisher model.
    > url = /publisher
    > method:
        > post : for creating the publisher
        > put : for updating the is_admin value of the publisher
        > get : for retrieving the publishers of a channel whose public_id was provided as a url param "channel"
        > delete : for deleting the publisher whose public_id was provided as a url param  "id"
    > data :
        > user (user profile public_id)
    > return = return a success message if no error
    > Note:
        > The authenticated user will be used as the owner of the channel
##### All Channels:
    > Description: This route is responsible for retrieving all channels
    > url = /channel/all
    > method:get
    > data :
        > name
        > description
    > return = return a success message if no error
    > Note:
        > The authenticated user will be used as the owner of the channel