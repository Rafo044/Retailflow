FROM astrocrpublic.azurecr.io/runtime:3.0-6

RUN pip install psycopg2-binary
RUN pip install pandas

RUN pip install sqlalchemy
