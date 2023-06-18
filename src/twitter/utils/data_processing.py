def get_document_text(doc):
    document_text = doc.page_content
    return document_text


def get_metadatas_from_documents(documents):
    metadatas = [document.metadata for document in documents]
    for metadata in metadatas:
        metadata["source"] = metadata["tweet_id"]
        metadata.pop("tweet_id")

    return metadatas


def get_texts_from_documents(documents):
    texts = [get_document_text(document) for document in documents]
    return texts
