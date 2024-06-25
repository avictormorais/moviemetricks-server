from models.Comment import Comment



def create_comment_controller(username, user_id, content, is_spoiler, media_id, userRole):
    comment_id = Comment.create_comment(username, user_id, content, is_spoiler, media_id, userRole)
    return comment_id





