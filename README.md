### Overview
This project is for the assignment in SSD, specifically Authorization. The assignment was to make a simple Rest API for a news website with different roles and permissions for said roles.

I have written mine in python with flask and JWT for authentication.

### Policy

**Editor can:**
- Edit, and delete articles.
- Edit and delete user comments.

**Writer / journalist can:**
- Create and edit their own articles.

**Subscriber / registered user can:**
- Comment on articles.

**Guest / public user can:**
- Read articles.
- Read comments.

### How to run
1. Clone the repository
2. Run `pip install -r requirements.txt` in terminal.
3. Run `main.py` - for me this ran on `http://127.0.0.1:5000/`
4. Test any commands using postman or similar programs.

### Commands
Variables are filled in, all you have to do is add the values <br>

Credentials you can use for logging in: <br>
| Username        | Password       |
|-----------------|----------------|
| EditorUser      | EditorPass     |
| WriterUser      | WriterPass     |
| OtherWriterUser | WriterPass     |
| SubscriberUser  | SubscriberPass |

`POST /login?username=&password=` <br>

Example article id: `418` to test get, update, and delete. <br>
`POST /postArticle?title=&content=` <br>
`GET /getArticle?article_id=` <br>
`PUT /updateArticle?article_id=&title=&content=` <br>
`DELETE /deleteArticle?article_id=` <br>

Example comment id: `0` to test get, update, and delete. <br>
`POST /postComment?content=&article_id=` <br>
`GET /getComment?comment_id=` <br>
`PUT /updateComment?comment_id=&content=` <br>
`DELETE /deleteComment?comment_id=` <br>