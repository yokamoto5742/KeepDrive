from unittest.mock import MagicMock

from service.docs_client import append_text


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
