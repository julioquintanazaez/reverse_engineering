# reverse_engineering



## Getting started


```
cd existing_repo
git remote add origin https://gitlab.com/julioquintanazaez/reverse_engineering.git
git branch -M main
git push -uf origin main
```

### To run the project
python manage.py makemigrations reverse_api
python manage.py migrate
python manage.py runserver


### Query by parameters

http://127.0.0.1:8000/reverse_api/get_engineering_genes/?gene=CYP2D6&gene=CYP1A1&alleles=CYP2D6,*8.001/*9.001&alleles=CYP2D6,*13/*15.001&alleles=CYP1A1,*2/*4&alleles=CYP1A1,*6/*8

http://127.0.0.1:8000/reverse_api/get_engineering_genes/?gene=CYP1A1&alleles=CYP1A1,*2/*3&alleles=CYP1A1,*4/*5
