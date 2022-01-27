from datetime import datetime
from configs.settings import app
from fastapi import Form, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
import json

from app.utils.logger import get_stream_logger
from model.request.comment import Comment, ReplyComment
from configs.settings import app, DB_NAME, MONGO_CLIENT, PROJECT_SECRET_KEY, COMMENT_COLLECTION, REPLY_COMMENT_COLLECTION

logger = get_stream_logger(__name__)

@app.post(
    path='/reply-comment', 
    tags=['Reply Comment'],
    name="Create reply comment"
)
async def create_reply_comment(
    content: str = Form(..., description='Nội dung comment'),
    comment_id: str = Form(..., description='ID của comment chính'),
    author_id: str = Form(..., description='Author ID của comment')
):
    "Tạo comment cho một bài đăng (hoặc là một event,...)"
    _inserted_id = None
    try:
        reply_comment = ReplyComment(
            content=content,
            comment_id=comment_id,
            author_id=author_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted=False
        )
        _inserted_id = MONGO_CLIENT[f'{DB_NAME}'][REPLY_COMMENT_COLLECTION].insert_one(
            jsonable_encoder(reply_comment)
        ).inserted_id
    except Exception as e:
        print("Have some errors: ",e)
        return JSONResponse(content={
            'msg': f'Create reply comment failed: {e}'
        }, status_code=status.HTTP_400_BAD_REQUEST)

    
    return JSONResponse(content={
            'id': str(_inserted_id),
            'msg': 'Created reply comment'
        }, status_code=status.HTTP_200_OK)
    

@app.get(
    path='/reply-comment', 
    tags=['Reply Comment'],
    name="Get reply comment"
)
async def get_reply_comment(
    comment_id: str = Form(..., description='Comment ID cần get')
):
    "Get comment cho một bài đăng (hoặc là một event,...)"
    reply_comments = MONGO_CLIENT[f'{DB_NAME}'][REPLY_COMMENT_COLLECTION].find({
        'comment_id': comment_id
    })
    reply_list_comments = list(reply_comments)
    return JSONResponse(content={
        'msg': 'Success',
        'data': json.loads(dumps(reply_list_comments))
    }, status_code=200)


@app.put(
    path='/reply-comment', 
    tags=['Reply Comment'],
    name="Update reply comment"
)
async def update_comment(
    id: str = Form(..., description="ID của reply comment cần update"),
    content: str = Form(..., description='Nội dung comment')
):
    "Cập nhật reply comment thuộc về 1 comment"
    try:
        MONGO_CLIENT[f'{DB_NAME}'][REPLY_COMMENT_COLLECTION].find_one_and_update(
            filter={'_id': ObjectId(id)},
            update={
                '$set': {
                    'content': content,
                    'updated_at': str(datetime.now())
                }
            }
        )
    except Exception as e:
        print(f"Have some errors: , {e}")
        return JSONResponse(content={
            'msg': f'Update reply comment failed: {e}'
        }, status_code=status.HTTP_400_BAD_REQUEST)
    
    return JSONResponse(content={
        'id': str(id),
        'msg': 'Updated reply comment'
    }, status_code=200)


@app.delete(
    path='/reply-comment', 
    tags=['Reply Comment'],
    name="Delete reply comment"
)
async def delete_comment(
    id: str = Form(..., description="ID của reply comment cần update")
):
    "Xoá reply comment thuộc về 1 comment"
    try:
        MONGO_CLIENT[f'{DB_NAME}'][REPLY_COMMENT_COLLECTION].find_one_and_update(
            filter={'_id': ObjectId(id)},
            update={
                '$set': {
                    'is_deleted': True,
                    'updated_at': str(datetime.now())
                }
            }
        )
    except Exception as e:
        print(f"Have some errors: , {e}")
        return JSONResponse(content={
            'msg': f'Delete reply comment failed: {e}'
        }, status_code=status.HTTP_400_BAD_REQUEST)
    
    return JSONResponse(content={
        'id': str(id),
        'msg': 'Deleted reply comment'
    }, status_code=200)
