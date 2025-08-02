import streamlit as st
import re
import xml.etree.ElementTree as ET
import logging
import traceback

logger = logging.getLogger(__name__)

def parse_evaluation_result(text):
    """解析評分結果中的 XML 內容"""
    try:
        logger.debug("開始解析評分結果")
        logger.debug(f"輸入文本: {text}")
        
        # 提取 XML 部分
        comments_match = re.search(r'<evaluation_comments>(.*?)</evaluation_comments>', text, re.DOTALL)
        scores_match = re.search(r'<evaluation_scores>(.*?)</evaluation_scores>', text, re.DOTALL)
        
        if not comments_match or not scores_match:
            logger.warning("未找到完整的 XML 結構")
            return {
                'usability_comment': 'N/A',
                'accuracy_comment': 'N/A',
                'completeness_comment': 'N/A',
                'overall_feedback': 'N/A',
                'usability_score': 0,
                'accuracy_score': 0,
                'completeness_score': 0,
                'total_score': 0
            }
        
        logger.debug("成功找到 XML 結構")
        
        # 構建完整的 XML 字符串
        comments_xml = f'<root>{comments_match.group(0)}</root>'
        scores_xml = f'<root>{scores_match.group(0)}</root>'
        
        logger.debug(f"評語 XML: {comments_xml}")
        logger.debug(f"分數 XML: {scores_xml}")
        
        # 解析評語
        try:
            comments_root = ET.fromstring(comments_xml)
            comments = {
                'usability_comment': comments_root.find('.//usability_comment').text.strip() if comments_root.find('.//usability_comment') is not None else 'N/A',
                'accuracy_comment': comments_root.find('.//accuracy_comment').text.strip() if comments_root.find('.//accuracy_comment') is not None else 'N/A',
                'completeness_comment': comments_root.find('.//completeness_comment').text.strip() if comments_root.find('.//completeness_comment') is not None else 'N/A',
                'overall_feedback': comments_root.find('.//overall_feedback').text.strip() if comments_root.find('.//overall_feedback') is not None else 'N/A'
            }
            logger.debug("成功解析評語")
        except ET.ParseError as e:
            logger.error(f"解析評語 XML 時發生錯誤: {str(e)}")
            comments = {
                'usability_comment': 'N/A',
                'accuracy_comment': 'N/A',
                'completeness_comment': 'N/A',
                'overall_feedback': 'N/A'
            }
        
        # 解析分數
        try:
            scores_root = ET.fromstring(scores_xml)
            scores = {
                'usability_score': float(scores_root.find('.//usability_score').text.strip().replace('分', '')) if scores_root.find('.//usability_score') is not None else 0,
                'accuracy_score': float(scores_root.find('.//accuracy_score').text.strip().replace('分', '')) if scores_root.find('.//accuracy_score') is not None else 0,
                'completeness_score': float(scores_root.find('.//completeness_score').text.strip().replace('分', '')) if scores_root.find('.//completeness_score') is not None else 0,
                'total_score': float(scores_root.find('.//total_score').text.strip().replace('分', '')) if scores_root.find('.//total_score') is not None else 0
            }
            logger.debug("成功解析分數")
        except ET.ParseError as e:
            logger.error(f"解析分數 XML 時發生錯誤: {str(e)}")
            scores = {
                'usability_score': 0,
                'accuracy_score': 0,
                'completeness_score': 0,
                'total_score': 0
            }
        
        # 合併結果
        result = {**comments, **scores}
        logger.debug(f"最終解析結果: {result}")
        return result
        
    except Exception as e:
        logger.error(f"解析評分結果時發生錯誤: {str(e)}")
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return {
            'usability_comment': 'N/A',
            'accuracy_comment': 'N/A',
            'completeness_comment': 'N/A',
            'overall_feedback': 'N/A',
            'usability_score': 0,
            'accuracy_score': 0,
            'completeness_score': 0,
            'total_score': 0
        } 