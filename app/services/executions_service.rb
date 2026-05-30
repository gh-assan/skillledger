class ExecutionsService
  VerificationError = Class.new(StandardError)

  def self.list(filters = {})
    executions = Execution.includes(:skill)
    executions = executions.where(skill_id: filters[:skill_id]) if filters[:skill_id].present?
    executions = executions.where(status: filters[:status]) if filters[:status].present?
    executions.order(created_at: :desc)
  end

  def self.get(id)
    Execution.includes(:skill).find(id)
  end

  def self.verify(id)
    execution = Execution.find(id)

    case execution.status
    when "completed"
      execution.update!(status: "verified", verified_at: Time.current)
      execution
    when "verified"
      raise VerificationError, "Execution is already verified"
    else
      raise VerificationError, "Cannot verify execution with status: #{execution.status}"
    end
  end
end
