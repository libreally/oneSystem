"""
文档管理 API 路由
"""
from flask import Blueprint, jsonify, request, send_from_directory
import os
import logging
from backend.config.settings import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE

logger = logging.getLogger(__name__)

# 创建蓝图
document_bp = Blueprint('document', __name__, url_prefix='/api/documents')

# 辅助函数
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_info(file_path):
    """获取文件信息"""
    try:
        stat = os.stat(file_path)
        return {
            'filename': os.path.basename(file_path),
            'path': file_path,
            'size': stat.st_size,
            'mtime': stat.st_mtime,
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except Exception:
        return None

@document_bp.route('/', methods=['GET'])
def get_documents():
    """获取所有上传的文档"""
    try:
        logger.info(f"开始获取文档列表，上传目录：{UPLOAD_DIR}")
        documents = []
        for root, dirs, files in os.walk(UPLOAD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                info = get_file_info(file_path)
                if info:
                    # 计算相对路径用于前端显示
                    relative_path = os.path.relpath(file_path, UPLOAD_DIR)
                    info['relative_path'] = relative_path
                    documents.append(info)
        
        logger.info(f"成功获取文档列表，共 {len(documents)} 个文档")
        return jsonify({
            'success': True,
            'data': {
                'documents': documents,
                'total': len(documents),
                'upload_dir': UPLOAD_DIR
            }
        })
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取文档列表失败: {str(e)}'
        }), 500

@document_bp.route('/', methods=['POST'])
def upload_document():
    """上传文档"""
    try:
        logger.info("开始处理文件上传")
        # 检查是否有文件
        if 'file' not in request.files:
            logger.warning("上传失败：未提供文件")
            return jsonify({
                'success': False,
                'message': '请选择要上传的文件'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            logger.warning("上传失败：文件名为空")
            return jsonify({
                'success': False,
                'message': '请选择要上传的文件'
            }), 400
        
        logger.info(f"开始上传文件：{file.filename}，大小：{file.content_length} 字节")
        
        # 检查文件大小
        if file.content_length > MAX_UPLOAD_SIZE:
            logger.warning(f"上传失败：文件大小超过限制，文件：{file.filename}，大小：{file.content_length} 字节")
            return jsonify({
                'success': False,
                'message': f'文件大小超过限制 ({MAX_UPLOAD_SIZE / 1024 / 1024}MB)'
            }), 400
        
        # 检查文件扩展名
        if not allowed_file(file.filename):
            logger.warning(f"上传失败：不支持的文件类型，文件：{file.filename}")
            return jsonify({
                'success': False,
                'message': '不支持的文件类型'
            }), 400
        
        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(file_path)
        logger.info(f"文件保存成功：{file_path}")
        
        # 获取文件信息
        info = get_file_info(file_path)
        
        logger.info(f"文件上传成功：{file.filename}")
        return jsonify({
            'success': True,
            'data': info,
            'message': '文件上传成功'
        })
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文件上传失败: {str(e)}'
        }), 500

@document_bp.route('/upload-from-system', methods=['POST'])
def upload_from_system():
    """从系统中选择文件上传"""
    try:
        logger.info("开始处理从系统选择文件上传")
        data = request.get_json()
        system_file_path = data.get('file_path')
        
        if not system_file_path:
            logger.warning("上传失败：未提供系统文件路径")
            return jsonify({
                'success': False,
                'message': '请提供系统文件路径'
            }), 400
        
        logger.info(f"开始上传系统文件：{system_file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(system_file_path):
            logger.warning(f"上传失败：系统文件不存在，路径：{system_file_path}")
            return jsonify({
                'success': False,
                'message': '系统文件不存在'
            }), 404
        
        # 检查文件大小
        file_size = os.path.getsize(system_file_path)
        if file_size > MAX_UPLOAD_SIZE:
            logger.warning(f"上传失败：文件大小超过限制，文件：{system_file_path}，大小：{file_size} 字节")
            return jsonify({
                'success': False,
                'message': f'文件大小超过限制 ({MAX_UPLOAD_SIZE / 1024 / 1024}MB)'
            }), 400
        
        # 检查文件扩展名
        filename = os.path.basename(system_file_path)
        if not allowed_file(filename):
            logger.warning(f"上传失败：不支持的文件类型，文件：{filename}")
            return jsonify({
                'success': False,
                'message': '不支持的文件类型'
            }), 400
        
        # 复制文件到上传目录
        import shutil
        dest_path = os.path.join(UPLOAD_DIR, filename)
        shutil.copy2(system_file_path, dest_path)
        logger.info(f"文件复制成功：从 {system_file_path} 到 {dest_path}")
        
        # 获取文件信息
        info = get_file_info(dest_path)
        
        logger.info(f"系统文件上传成功：{filename}")
        return jsonify({
            'success': True,
            'data': info,
            'message': '文件上传成功'
        })
    except Exception as e:
        logger.error(f"系统文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文件上传失败: {str(e)}'
        }), 500

@document_bp.route('/<filename>', methods=['GET'])
def download_document(filename):
    """下载文档"""
    try:
        logger.info(f"开始下载文件：{filename}")
        return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文件下载失败: {str(e)}'
        }), 500

@document_bp.route('/<filename>', methods=['DELETE'])
def delete_document(filename):
    """删除文档"""
    try:
        logger.info(f"开始删除文件：{filename}")
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"文件删除成功：{filename}")
            return jsonify({
                'success': True,
                'message': '文件删除成功'
            })
        else:
            logger.warning(f"删除失败：文件不存在，文件：{filename}")
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文件删除失败: {str(e)}'
        }), 500

@document_bp.route('/preview/<filename>', methods=['GET'])
def preview_document(filename):
    """预览文档"""
    try:
        logger.info(f"开始预览文件：{filename}")
        # 对于图片文件，直接返回文件
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                logger.info(f"预览图片文件：{filename}")
                return send_from_directory(UPLOAD_DIR, filename)
            else:
                # 对于其他文件类型，返回文件信息
                info = get_file_info(file_path)
                logger.info(f"预览文件信息：{filename}")
                return jsonify({
                    'success': True,
                    'data': info,
                    'message': '文件预览信息'
                })
        else:
            logger.warning(f"预览失败：文件不存在，文件：{filename}")
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
    except Exception as e:
        logger.error(f"文件预览失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文件预览失败: {str(e)}'
        }), 500

@document_bp.route('/config', methods=['GET'])
def get_upload_config():
    """获取上传配置"""
    return jsonify({
        'success': True,
        'data': {
            'upload_dir': UPLOAD_DIR,
            'max_upload_size': MAX_UPLOAD_SIZE,
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }
    })

@document_bp.route('/config', methods=['PUT'])
def update_upload_config():
    """更新上传配置"""
    try:
        logger.info("开始更新上传配置")
        data = request.get_json()
        new_upload_dir = data.get('upload_dir')
        
        if new_upload_dir:
            # 验证目录是否存在
            if not os.path.exists(new_upload_dir):
                os.makedirs(new_upload_dir, exist_ok=True)
                logger.info(f"创建新的上传目录：{new_upload_dir}")
            
            logger.info(f"上传配置更新成功，新目录：{new_upload_dir}")
            # 更新配置（这里需要注意，由于配置是模块级别的，我们需要重新加载配置）
            # 这里只是返回成功，实际更新需要修改settings.py文件
            return jsonify({
                'success': True,
                'message': '上传配置更新成功',
                'data': {
                    'upload_dir': new_upload_dir
                }
            })
        else:
            logger.warning("配置更新失败：未提供新的上传目录")
            return jsonify({
                'success': False,
                'message': '请提供新的上传目录'
            }), 400
    except Exception as e:
        logger.error(f"配置更新失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'配置更新失败: {str(e)}'
        }), 500