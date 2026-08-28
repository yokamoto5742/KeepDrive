from typing import Any


def append_text(docs: Any, document_id: str, text: str) -> None:
    """ドキュメント末尾へテキストを追記する（仕様書 §5-4-d）。"""
    end_index = _fetch_body_end_index(docs, document_id)

    docs.documents().batchUpdate(
        documentId=document_id,
        body={
            'requests': [
                {
                    'insertText': {
                        # 本文末尾には必ず改行があるため、その直前に挿入する
                        'location': {'index': end_index - 1},
                        'text': text,
                    }
                }
            ]
        },
    ).execute()


def extract_text(docs: Any, document_id: str) -> str:
    """ドキュメント本文を段落単位のプレーンテキストとして取り出す。"""
    document = docs.documents().get(
        documentId=document_id, fields='body.content'
    ).execute()

    return ''.join(
        run['textRun']['content']
        for element in document['body']['content']
        for run in element.get('paragraph', {}).get('elements', [])
        if 'textRun' in run
    )


def _fetch_body_end_index(docs: Any, document_id: str) -> int:
    document = docs.documents().get(
        documentId=document_id, fields='body.content'
    ).execute()
    content = document['body']['content']
    return content[-1]['endIndex']
