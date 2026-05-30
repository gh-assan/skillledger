class Execution < ApplicationRecord
  belongs_to :skill

  validates :status, presence: true, inclusion: { in: %w[pending running completed failed verified] }

  scope :pending, -> { where(status: "pending") }
  scope :running, -> { where(status: "running") }
  scope :completed, -> { where(status: "completed") }
  scope :failed, -> { where(status: "failed") }
  scope :verified, -> { where(status: "verified") }
end
