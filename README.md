# Educational project Foodgram
## Discription

This project is a adapted to Docker and Docker-cpmpose api_yamdb project

### API Documentation:
Example and documentation - [http://51.250.102.154/api/docs/](http://51.250.102.154/api/docs/)

### Project api_yamdb description

Created on the basis of the framework [Django REST Framework (DRF)](https://github.com/ilyachch/django-rest-framework-rusdoc)

> The Foodgram project collects user recipes. You can view and filter recipes by tags, add some of them to the shopping cart, download shopping cart list as a file, add recipe to the favorite list.
> Registred members can add their own recipes to the site.

## Technologies

- Python 3.7
- Django 3.2.15
- Django Rest Framework==3.12.4
- Docker version 20.10.24
- Docker compose 3.8
- PostgreSQL 15.3
- Nginx 1.19.3

## Start Project 
Clone the repository and go to it on the command line:

```
git clone git@github.com:FedOK007/Foodgram_project_DRF.git
```

### **Run images with docker-copmpose**

Go to the directory infra

```
cd infra
```

Make .env file use .env_example and fill correct parameters

```
mv .env_example .env
nano .env
```

Run docker compose up

```
docker compose up
```

Next make migrations and run collectstatic inside the Image "web"

```
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --no-input
```

## UI Access

Your app is available at: http://localhost

## Documentation Api (local)
Documentaion is available at http://127.0.0.1:8000/api/docs/ or http://localhos/api/docs/ for docker-compose installation.

### Request examples

> Get (http://127.0.0.1:8000/api/recipes/):

```
Header:
Authorization: Token <token from /api/auth/token/login/>

Body:
{
    "tags": [
        2,
        1
    ],
    "ingredients": [
        {
            "id": 2,
            "amount": 11
        },
        {
            "id": 21,
            "amount": 12
        }
    ],
    "name": "Рецепт api 2",
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "text": "Текст рецепта 2",
    "cooking_time": 230
}
```
## Authors

[FedOK007](https://github.com/FedOK007)