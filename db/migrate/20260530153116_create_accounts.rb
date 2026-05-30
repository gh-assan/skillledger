class CreateAccounts < ActiveRecord::Migration[8.1]
  def change
    create_table :accounts do |t|
      t.string :name, null: false
      t.decimal :balance, precision: 12, scale: 2, default: 0.0

      t.timestamps
    end
    add_index :accounts, :name, unique: true
  end
end
