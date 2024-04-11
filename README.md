# url-shortener
MercadoLibre technical challenge project.


# Application Overview

The main app is built in Python 3.9 using [FastAPI](https://fastapi.tiangolo.com/) and [OpenTelemetry](https://opentelemetry.io/).

The storage is managed by a [Redis](https://redis.io) container.

<img title="a title" alt="Alt text" src="./assets/architecture.jpeg">


# API Endopoints

The endpoints to administrate URLs are as follows:

| Endpoint      | Method | Description                                        | Input                           | Output                            |
|---------------|--------|----------------------------------------------------|---------------------------------|-----------------------------------|
| /url          | POST   | To create shortened URLs.                          | The target URL.                 | The details of the shortened URL. |
| /info{code}   | GET    | To get shortened URL info.                         | The previously genereated code. | The details of the shortened URL. |
| /{code}       | GET    | Forward short URL to original URL.                 |                                 |                                   |
| /delete/{code}| DELETE | Delete (deactivate) the shortened URL by its code. |                                 |                                   |

