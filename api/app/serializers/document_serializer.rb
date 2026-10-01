class DocumentSerializer
  def self.call(document)
    {
      id: document.id,
      filename: document.filename,
      contentType: document.content_type,
      byteSize: document.byte_size,
      status: document.status,
      kind: document.kind,
      chunksCount: document.chunks_count,
      charactersCount: document.characters_count,
      extractedPreview: document.extracted_preview,
      error: document.error,
      createdAt: document.created_at.iso8601
    }
  end
end
