class Document < ApplicationRecord
  STATUSES = %w[pending processing completed failed].freeze

  has_one_attached :file

  validates :filename, :content_type, :byte_size, presence: true
  validates :status, inclusion: { in: STATUSES }

  scope :recent, -> { order(created_at: :desc) }

  def self.from_upload(upload)
    document = new(
      filename: upload.original_filename,
      content_type: upload.content_type.presence || "application/octet-stream",
      byte_size: upload.size
    )
    document.file.attach(upload)
    document
  end

  def processing!
    update!(status: "processing")
  end

  def failed!(message)
    update!(status: "failed", error: message)
  end
end
