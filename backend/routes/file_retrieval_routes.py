"""
本地文件检索 API 路由
"""
from flask import Blueprint, jsonify, request
from backend.services.file_retrieval_service import file_retrieval_service

file_retrieval_bp = Blueprint('file_retrieval', __name__, url_prefix='/api/files')


@file_retrieval_bp.route('/search', methods=['GET'])
def search_files():
    """搜索文件"""
    query = request.args.get('query', '')
    file_types = request.args.getlist('file_type')
    max_results = int(request.args.get('max_results', 20))
    
    if not query and not file_types:
        return jsonify({
            'success': False,
            'message': '请提供查询关键词或文件类型'
        }), 400
    
    results = file_retrieval_service.search_files(
        query=query if query else None,
        file_types=file_types if file_types else None,
        max_results=max_results
    )
    
    return jsonify({
        'success': True,
        'data': {
            'files': results,
            'total': len(results),
            'query': query
        }
    })


@file_retrieval_bp.route('/info', methods=['GET'])
def get_file_info():
    """获取文件信息"""
    file_path = request.args.get('path')
    
    if not file_path:
        return jsonify({
            'success': False,
            'message': '请提供文件路径'
        }), 400
    
    info = file_retrieval_service.get_file_info(file_path)
    
    if info:
        return jsonify({
            'success': True,
            'data': info
        })
    else:
        return jsonify({
            'success': False,
            'message': '文件不存在'
        }), 404


@file_retrieval_bp.route('/content', methods=['GET'])
def get_file_content():
    """获取文件内容（仅文本类文件）"""
    file_path = request.args.get('path')
    max_length = int(request.args.get('max_length', 10000))
    
    if not file_path:
        return jsonify({
            'success': False,
            'message': '请提供文件路径'
        }), 400
    
    content = file_retrieval_service.read_file_content(file_path, max_length)
    
    if content is not None:
        return jsonify({
            'success': True,
            'data': {
                'file_path': file_path,
                'content': content,
                'length': len(content)
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '无法读取文件内容，可能文件不存在或不支持该格式'
        }), 400


@file_retrieval_bp.route('/knowledge-base', methods=['POST'])
def add_to_knowledge_base():
    """添加文件到会话知识库"""
    data = request.get_json()
    
    session_id = data.get('session_id')
    file_paths = data.get('file_paths', [])
    
    if not session_id:
        return jsonify({
            'success': False,
            'message': '请提供会话 ID'
        }), 400
    
    if not file_paths:
        return jsonify({
            'success': False,
            'message': '请提供文件路径列表'
        }), 400
    
    success = file_retrieval_service.add_to_session_knowledge_base(session_id, file_paths)
    
    return jsonify({
        'success': success,
        'message': f'成功添加 {len(file_paths)} 个文件到知识库' if success else '添加失败'
    })


@file_retrieval_bp.route('/knowledge-base', methods=['GET'])
def get_knowledge_base():
    """获取会话知识库"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'message': '请提供会话 ID'
        }), 400
    
    kb = file_retrieval_service.get_session_knowledge_base(session_id)
    
    return jsonify({
        'success': True,
        'data': kb
    })


@file_retrieval_bp.route('/knowledge-base', methods=['DELETE'])
def clear_knowledge_base():
    """清空会话知识库"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'message': '请提供会话 ID'
        }), 400
    
    success = file_retrieval_service.clear_session_knowledge_base(session_id)
    
    return jsonify({
        'success': success,
        'message': '知识库已清空' if success else '知识库不存在'
    })


@file_retrieval_bp.route('/knowledge-base/search', methods=['GET'])
def search_in_knowledge_base():
    """在会话知识库中搜索"""
    session_id = request.args.get('session_id')
    query = request.args.get('query', '')
    
    if not session_id:
        return jsonify({
            'success': False,
            'message': '请提供会话 ID'
        }), 400
    
    results = file_retrieval_service.search_in_session_knowledge_base(
        session_id=session_id,
        query=query if query else None
    )
    
    return jsonify({
        'success': True,
        'data': {
            'files': results,
            'total': len(results)
        }
    })


@file_retrieval_bp.route('/types', methods=['GET'])
def get_supported_types():
    """获取支持的文件类型"""
    return jsonify({
        'success': True,
        'data': {
            'supported_extensions': list(file_retrieval_service.supported_extensions),
            'readable_extensions': ['.txt', '.md', '.json', '.xml', '.yaml', '.yml', '.csv']
        }
    })
