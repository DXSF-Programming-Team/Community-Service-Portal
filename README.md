If you want to run this website on your own computer, follow this guide.



This website uses PostgreSQL to store information.

To create your own local database instance, first install Docker here:

https://www.docker.com/products/docker-desktop/

Then, in the command line, download the latest PostgreSQL image:

```bash
docker pull postgres
```

Run this in the command line to create the database

```bash
docker run --name community-service-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=app_db -p 5432:5432 -d postgres
```

You can verify the container is running with

```bash
docker ps
```

Initialize the database

```bash
python init_db.py
```

If this gives you an error, it is likely you have not installed the required packages. First, (if you haven't already), create a virtual environment:

```bash
python -m venv venv
```

Then install the necessary packages.

```bash
pip install -r requirements.txt
```




P.S.-

If you ever want to open the SQL interactive mode to manually edit the database, run

```bash
docker exec -it fakemon-db psql -U postgres -d app_db
```

See https://www.geeksforgeeks.org/sql/sql-cheat-sheet/ for a quick list of commands.