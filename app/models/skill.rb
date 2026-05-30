class Skill < ApplicationRecord
  has_many :executions, dependent: :destroy

  validates :name, presence: true, uniqueness: true
  validates :version, numericality: { only_integer: true, greater_than: 0 }
end
