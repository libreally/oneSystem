"""
WPS 集成路由
支持 WPS 相关的 API 端点
"""
from flask import Blueprint, jsonify, request
from backend.services.wps_integration_service import wps_integration_service

wps_bp = Blueprint('wps', __name__, url_prefix='/api/wps')


@wps_bp.route('/active-document', methods=['GET'])
def get_active_document():
    """
    获取当前活动的 WPS 文档
    """
    try:
        document = wps_integration_service.get_active_document()
        if document:
            return jsonify({
                'success': True,
                'data': document
            })
        else:
            return jsonify({
                'success': False,
                'message': '没有活动的 WPS 文档'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取活动文档失败: {str(e)}'
        }), 500


@wps_bp.route('/open-file', methods=['POST'])
def open_file():
    """
    打开指定文件
    """
    data = request.get_json()
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({
            'success': False,
            'message': '文件路径不能为空'
        }), 400
    
    try:
        result = wps_integration_service.open_file(file_path)
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '打开文件失败')
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'打开文件失败: {str(e)}'
        }), 500


@wps_bp.route('/process/word', methods=['POST'])
def process_word_document():
    """
    处理 Word 文档
    """
    data = request.get_json()
    file_path = data.get('file_path')
    operation = data.get('operation')
    params = data.get('params', {})
    
    if not file_path or not operation:
        return jsonify({
            'success': False,
            'message': '文件路径和操作类型不能为空'
        }), 400
    
    try:
        result = wps_integration_service.process_word_document(file_path, operation, params)
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '处理文档失败')
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'处理文档失败: {str(e)}'
        }), 500


@wps_bp.route('/process/excel', methods=['POST'])
def process_excel_document():
    """
    处理 Excel 文档
    """
    data = request.get_json()
    file_path = data.get('file_path')
    operation = data.get('operation')
    params = data.get('params', {})
    
    if not file_path or not operation:
        return jsonify({
            'success': False,
            'message': '文件路径和操作类型不能为空'
        }), 400
    
    try:
        result = wps_integration_service.process_excel_document(file_path, operation, params)
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '处理文档失败')
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'处理文档失败: {str(e)}'
        }), 500


@wps_bp.route('/close-apps', methods=['POST'])
def close_wps_apps():
    """
    关闭所有 WPS 应用
    """
    try:
        wps_integration_service.close_applications()
        return jsonify({
            'success': True,
            'message': 'WPS 应用已关闭'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'关闭 WPS 应用失败: {str(e)}'
        }), 500
