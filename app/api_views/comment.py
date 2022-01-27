from datetime import datetime
from configs.settings import app
from fastapi import Form, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
import json

from app.utils.logger import get_stream_logger
from model.request.comment import Comment
from configs.settings import app, DB_NAME, MONGO_CLIENT, PROJECT_SECRET_KEY, COMMENT_COLLECTION, REPLY_COMMENT_COLLECTION

logger = get_stream_logger(__name__)

@app.post(
    path='/comment', 
    tags=['Comment'],
    name="Create comment"
)
async def create_comment(
    content: str = Form(..., description='Nội dung comment'),
    target_id: str = Form(..., description='Target ID của comment'),
    author_id: str = Form(..., description='Author ID của comment')
):
    "Tạo comment cho một bài đăng (hoặc là một event,...)"
    _inserted_id = None
    try:
        comment = Comment(
            content=content,
            target_id=target_id,
            author_id=author_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted=False,
            like=0
        )
        _inserted_id = MONGO_CLIENT[f'{DB_NAME}'][COMMENT_COLLECTION].insert_one(
            jsonable_encoder(comment)
        ).inserted_id
    except Exception as e:
        print("Have some errors: ",e)
        return JSONResponse(content={
            'msg': f'Create comment failed: {e}'
        }, status_code=status.HTTP_400_BAD_REQUEST)

    
    return JSONResponse(content={
            'id': str(_inserted_id),
            'msg': 'Created comment'
        }, status_code=status.HTTP_200_OK)
    

@app.get(
    path='/comment', 
    tags=['Comment'],
    name="Get comment"
)
async def get_comment(
    target_id: str = Form(..., description='Target ID cần get')
):
    "Get comment cho một bài đăng (hoặc là một event,...)"
    comments = MONGO_CLIENT[f'{DB_NAME}'][COMMENT_COLLECTION].find({
        'target_id': target_id
    })
    list_comments = list(comments)
    print(loads(dumps(list_comments)))
    return JSONResponse(content={
        'msg': 'Success',
        'data': json.loads(dumps(list_comments))
    }, status_code=200)


@app.put(
    path='/comment', 
    tags=['Comment'],
    name="Update comment"
)
async def update_comment(
    id: str = Form(..., description="ID của comment cần update"),
    content: str = Form(..., description='Nội dung comment'), 
    like: int = Form(..., description="Số lượng like của comment")
):
    "Cập nhật comment cho một bài đăng (hoặc là một event,...)"
    try:
        MONGO_CLIENT[f'{DB_NAME}'][COMMENT_COLLECTION].find_one_and_update(
            filter={'_id': ObjectId(id)},
            update={
                '$set': {
                    'content': content,
                    'updated_at': str(datetime.now()),
                    'like': like
                }
            }
        )
    except Exception as e:
        print(f"Have some errors: , {e}")
        return JSONResponse(content={
            'msg': f'Update comment failed: {e}'
        }, status_code=status.HTTP_400_BAD_REQUEST)
    
    return JSONResponse(content={
        'id': str(id),
        'msg': 'Updated comment'
    }, status_code=200)


@app.delete(
    path='/comment', 
    tags=['Comment'],
    name="Delete comment"
)
async def delete_comment(
    id: str = Form(..., description='ID của comment cần xoá')
):
    "Xoá comment cho một bài đăng (hoặc là một event,...) -> không xoá 1 record, chỉ update deleted_flag trong DB"
    try:
        MONGO_CLIENT[f'{DB_NAME}'][COMMENT_COLLECTION].find_one_and_update(
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
            'msg': f'Delete comment failed: {e}'
        }, status_code=status.HTTP_400_BAD_REQUEST)
    
    return JSONResponse(content={
        'id': str(id),
        'msg': 'Deleted comment'
    }, status_code=200)