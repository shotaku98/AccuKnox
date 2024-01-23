# Social Network Django Project

This Django project is a social networking application that includes various functionalities such as user authentication, friend requests, and listing friends.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Dockerization](#dockerization)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Django Settings](#django-settings)
- [Models](#models)
- [Views](#views)
- [Dockerfile](#dockerfile)
- [Docker Compose](#docker-compose)

## Prerequisites

Make sure you have the following prerequisites installed on your system:
I have currently included the db here but if required the db can be mapped in docker env and connected as well :)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/shotaku98/AccuKnox
   cd social_network
   ```

   ```bash
   docker-compose up --build


## Models

The project includes the following Django models:

### CustomUser:

- Fields:
  - `id`: UUID primary key
  - `email`: EmailField (unique)
  - `name`: CharField
  - `password`: CharField
  - `friends`: ManyToManyField to itself
- String representation: Returns the email of the user.

### FriendRequest:

- Fields:
  - `from_user`: ForeignKey to `CustomUser` (sent friend requests)
  - `to_user`: ForeignKey to `CustomUser` (received friend requests)
  - `is_accepted`: BooleanField (default=False)
  - `created_at`: DateTimeField (auto_now_add=True)

## Views

The project includes the following Django views:

### UserRegistrationView:

- Endpoint: `/api/register/`
- Method: POST
- Description: Register a new user.

### UserLoginView:

- Endpoint: `/api/login/`
- Method: POST
- Description: Log in a user and generate JWT tokens.

### UserLogoutView:

- Endpoint: `/api/logout/`
- Method: POST
- Description: Log out a user and delete JWT cookies.

### UserStatusView:

- Endpoint: `/api/status/`
- Method: GET
- Description: Check the login status of a user.

### UserSearchView:

- Endpoint: `/api/search/`
- Method: GET
- Description: Search for users by email or name.

### FriendRequestView:

- Endpoint: `/api/friend-request/`
- Methods: POST, GET, PATCH, DELETE
- Description: Manage friend requests, send, accept, reject, or delete.

### FriendsListView:

- Endpoint: `/api/friends/`
- Method: GET
- Description: Get the list of friends for a logged-in user.