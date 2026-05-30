class CreateSkills < ActiveRecord::Migration[8.1]
  def change
    create_table :skills do |t|
      t.string :name, null: false
      t.text :description
      t.text :prompt
      t.json :input_schema
      t.json :output_schema
      t.integer :version, default: 1
      t.json :metadata, default: {}

      t.timestamps
    end
    add_index :skills, :name, unique: true
  end
end
