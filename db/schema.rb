# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_05_30_153116) do
  create_table "accounts", force: :cascade do |t|
    t.decimal "balance", precision: 12, scale: 2, default: "0.0"
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_accounts_on_name", unique: true
  end

  create_table "executions", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.text "error_message"
    t.datetime "executed_at"
    t.json "input", default: {}
    t.json "output"
    t.integer "skill_id", null: false
    t.string "status", default: "pending", null: false
    t.datetime "updated_at", null: false
    t.datetime "verified_at"
    t.index ["skill_id"], name: "index_executions_on_skill_id"
    t.index ["status"], name: "index_executions_on_status"
  end

  create_table "skills", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.text "description"
    t.json "input_schema"
    t.json "metadata", default: {}
    t.string "name", null: false
    t.json "output_schema"
    t.text "prompt"
    t.datetime "updated_at", null: false
    t.integer "version", default: 1
    t.index ["name"], name: "index_skills_on_name", unique: true
  end

  add_foreign_key "executions", "skills"
end
