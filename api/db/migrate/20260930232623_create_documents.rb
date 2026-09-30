class CreateDocuments < ActiveRecord::Migration[8.1]
  def change
    create_table :documents do |t|
      t.string :filename, null: false
      t.string :content_type, null: false
      t.bigint :byte_size, null: false
      t.string :status, null: false, default: "pending"
      t.string :kind
      t.integer :chunks_count
      t.integer :characters_count
      t.text :extracted_preview
      t.text :error

      t.timestamps
    end

    add_index :documents, :status
  end
end
