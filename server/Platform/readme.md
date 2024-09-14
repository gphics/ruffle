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