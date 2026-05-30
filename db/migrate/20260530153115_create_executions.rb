class CreateExecutions < ActiveRecord::Migration[8.1]
  def change
    create_table :executions do |t|
      t.references :skill, null: false, foreign_key: true
      t.json :input, default: {}
      t.json :output
      t.string :status, null: false, default: 'pending'
      t.text :error_message
      t.datetime :executed_at
      t.datetime :verified_at

      t.timestamps
    end
    add_index :executions, :status
  end
end
