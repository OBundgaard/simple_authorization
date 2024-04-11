import datetime
from datetime import timedelta
from flask import Flask, jsonify, request
from database_utilities import *
import jwt

# Initialze the flask app
app = Flask(__name__)

# Database
# CHECK README FOR PASSWORDS
database = {
    "users": [
        User(0, "EditorUser", "40fcedc019ba468ad5e40afae682f206fb2f84bd992e76012a954b6837db6d49", 3),
        User(1, "WriterUser", "2bb26d6547669cd94498bff59ba95f43634af079f07021b6b041aed8028f616a", 2),
        User(2, "OtherWriterUser", "2bb26d6547669cd94498bff59ba95f43634af079f07021b6b041aed8028f616a", 2),
        User(3, "SubscriberUser", "dbc23bb5d248475959a68ddcbcb5bdf879f7471868f86d71cdd2b29c5b74986f", 1)
    ],
    "articles": [
        Article(418, "I'm a teapot", "A java developer tried to brew coffee in a C# developer's teapot, sources "
                                     "report that it was supposed to be an April Fools prank but it went wrong.", 1,
                datetime(1998, 4, 1, 12, 43, 47)
                )
    ],
    "comments": [
        Comment(0, "Some people in this day and age will predict that we have flying cars in the future, "
                   "but I believe that we will have developers making fun of this april fools prank!", 418, 3,
                datetime(1998, 4, 1, 13, 23, 56))
    ]
}


# region User route
@app.route('/login', methods=['POST'])
def login():
    args = request.args

    try:
        # Check for the user
        for user in database['users']:
            if user.username == args['username'] and user.password_hash == hash_string(args['password']):
                # The user exists, therefore generate the JWT token and return it
                return jsonify({
                    'token': jwt.encode({
                        'role_id': user.role_id,
                        'user_id': user.user_id,
                        'exp': datetime.now() + timedelta(hours=2)
                    },
                        'secret',
                        algorithm='HS256'
                    )
                }), 200

            # The user does exist, but the password is incorrect, return error.
            if user.username == args['username'] and user.password_hash != hash_string(args['password']):
                return jsonify({'error': 'Unauthorized'}), 401

        # The user does not exist, return 404
        return jsonify({
            'error': 'User not found',
            'message': 'A user with this username does not exist'
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# endregion

# region Article routes
@app.route('/postArticle', methods=['POST'])
def post_article():
    args = request.args
    headers = request.headers

    try:
        # Valdate the token, and ensure the correct role is doing the call
        token = validate_jwt_token(headers['Authorization'])
        if not token or token['role_id'] != 2:
            return jsonify({'error': 'Unauthorized'}), 401

        # Generate ID for our new article
        existing_ids = {article.article_id for article in database['articles']}
        new_id = 0
        while new_id in existing_ids:
            new_id += 1

        # Add the article to the "database"
        database['articles'].append(Article(
            article_id=new_id,
            title=args['title'],
            content=args['content'],
            author_id=int(token['user_id']),
            created_at=datetime.now()
        ))

        return jsonify({'success': 'Article posted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/getArticle', methods=['GET'])
def get_article():
    args = request.args

    try:
        # Check for the article
        for article in database['articles']:
            if article.article_id == int(args['article_id']):
                # Return the article
                return jsonify({
                    'article_id': article.article_id,
                    'title': article.title,
                    'content': article.content,
                    'author_id': article.author_id,
                    'created_at': article.created_at
                }), 200

        # Fallback if the article was not found
        return jsonify({
            'error': 'Article not found',
            'message': 'Article does not exist or an incorrect article id has been provided'
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/updateArticle', methods=['PUT'])
def update_article():
    args = request.args
    headers = request.headers

    try:
        # Find the article
        selected_article = None
        selected_article_index = -1
        for index, article in enumerate(database['articles']):
            if article.article_id == int(args['article_id']):
                selected_article = article
                selected_article_index = index
                break

        if selected_article is None:
            return jsonify({
                'error': 'Article not found',
                'message': 'Article does not exist or an incorrect article id has been provided'
            }), 404

        # Validate the token
        token = validate_jwt_token(headers['Authorization'])
        if not token or token['role_id'] == 1 or (token['role_id'] == 2 and token['user_id'] != selected_article.author_id):
            return jsonify({'error': 'Unauthorized'}), 401

        # Update the article
        selected_article.title = args['title']
        selected_article.content = args['content']

        database['articles'][selected_article_index] = selected_article

        return jsonify({'success': 'Article updated'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/deleteArticle', methods=['DELETE'])
def delete_article():
    args = request.args
    headers = request.headers

    try:
        # Find the article
        article_index = -1
        for index, article in enumerate(database['articles']):
            if article.article_id == int(args['article_id']):
                article_index = index
                break

        if article_index == -1:
            return jsonify({
                'error': 'Article not found',
                'message': 'Article does not exist or an incorrect article id has been provided'
            }), 404

        # Validate the token
        token = validate_jwt_token(headers['Authorization'])
        if not token or token['role_id'] != 3:
            return jsonify({'error': 'Unauthorized'}), 401

        # Delete the article
        database['articles'].pop(article_index)

        return jsonify({'success': 'Article deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# endregion

# region Comment routes
@app.route('/postComment', methods=['POST'])
def post_comment():
    args = request.args
    headers = request.headers

    try:
        # Validate the token
        token = validate_jwt_token(headers['Authorization'])
        if not token or token['role_id'] != 1:
            return jsonify({'error': 'Unauthorized'}), 401

        # Generate ID for our new comment
        existing_ids = {comment.comment_id for comment in database['comments']}
        new_id = 0
        while new_id in existing_ids:
            new_id += 1

        # Add the comment to the "database"
        database['comments'].append(Comment(
            comment_id=new_id,
            content=args['content'],
            article_id=int(args['article_id']),
            user_id=int(token['user_id']),
            created_at=datetime.now()
        ))

        return jsonify({'success': 'Article posted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/getComment', methods=['GET'])
def get_comment():
    args = request.args

    try:
        # Check for the comment
        for comment in database['comments']:
            if comment.comment_id == int(args['comment_id']):
                # Return the comment if found
                return jsonify({
                    'comment_id': comment.comment_id,
                    'content': comment.content,
                    'article_id': comment.article_id,
                    'user_id': comment.user_id,
                    'created_at': comment.created_at
                }), 200

        # Fallback if the comment was not found
        return jsonify({
            'error': 'Comment not found',
            'message': 'Comment does not exist or an incorrect comment id has been provided'
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/updateComment', methods=['PUT'])
def update_comment():
    args = request.args
    headers = request.headers

    try:
        # Find the article
        selected_comment = None
        selected_comment_index = -1
        for index, comment in enumerate(database['comments']):
            if comment.comment_id == int(args['comment_id']):
                selected_comment = comment
                selected_comment_index = index
                break

        if selected_comment is None:
            return jsonify({
                'error': 'Comment not found',
                'message': 'Comment does not exist or an incorrect Comment id has been provided'
            }), 404

        # Validate the token
        token = validate_jwt_token(headers['Authorization'])
        if not token or token['role_id'] != 3:
            return jsonify({'error': 'Unauthorized'}), 401

        # Update the article
        selected_comment.content = args['content']

        database['comments'][selected_comment_index] = selected_comment

        return jsonify({'success': 'Comment updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/deleteComment', methods=['DELETE'])
def delete_comment():
    args = request.args
    headers = request.headers

    try:
        # Find the article
        comment_index = -1
        for index, comment in enumerate(database['comments']):
            if comment.comment_id == int(args['comment_id']):
                comment_index = index
                break

        if comment_index == -1:
            return jsonify({
                'error': 'Comment not found',
                'message': 'Comment does not exist or an incorrect comment id has been provided'
            }), 404

        # Validate the token
        token = validate_jwt_token(headers['Authorization'])
        if not token or token['role_id'] != 3:
            return jsonify({'error': 'Unauthorized'}), 401

        # Delete the comment
        database['comments'].pop(comment_index)

        return jsonify({'success': 'Comment deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
# endregion


if __name__ == '__main__':
    app.run(debug=True)
