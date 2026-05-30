class HealthService
  def self.check
    {
      status: "ok",
      timestamp: Time.current.iso8601,
      database: database_connected?,
      version: "1.0.0"
    }
  end

  def self.database_connected?
    ActiveRecord::Base.connection.execute("SELECT 1")
    true
  rescue StandardError
    false
  end
end
