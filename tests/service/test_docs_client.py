from unittest.mock import MagicMock

from service.docs_client import append_text, extract_text


def test_append_text_inserts_before_trailing_newline() -> None:
    docs = MagicMock()
    docs.documents().get().execute.return_value = {
        'body': {'content': [{'endIndex': 1}, {'endIndex': 42}]}
    }
    docs.documents().batchUpdate.reset_mock()

    append_text(docs, 'doc-1', '牛乳\n')

    request = docs.documents().batchUpdate.call_args.kwargs['body']['requests'][0]
    assert request['insertText']['location']['index'] == 41
    assert request['insertText']['text'] == '牛乳\n'


def test_append_text_targets_given_document() -> None:
    docs = MagicMock()
    docs.documents().get().execute.return_value = {
        'body': {'content': [{'endIndex': 1}]}
    }
    docs.documents().batchUpdate.reset_mock()

    append_text(docs, 'doc-9', 'テキスト\n')

    assert docs.documents().batchUpdate.call_args.kwargs['documentId'] == 'doc-9'


def build_docs_with_paragraphs(*texts: str) -> MagicMock:
    docs = MagicMock()
    docs.documents().get().execute.return_value = {
        'body': {
            'content': [
                {'paragraph': {'elements': [{'textRun': {'content': text}}]}}
                for text in texts
            ]
        }
    }
    return docs


def test_extract_text_joins_paragraph_text_runs() -> None:
    docs = build_docs_with_paragraphs('一行目\n', '二行目\n')

    assert extract_text(docs, 'doc-1') == '一行目\n二行目\n'


def test_extract_text_skips_non_text_elements() -> None:
    docs = MagicMock()
    docs.documents().get().execute.return_value = {
        'body': {
            'content': [
                {'sectionBreak': {}},
                {
                    'paragraph': {
                        'elements': [
                            {'inlineObjectElement': {}},
                            {'textRun': {'content': '本文\n'}},
                        ]
                    }
                },
            ]
        }
    }

    assert extract_text(docs, 'doc-1') == '本文\n'
