class SkillsService
  def self.list(filters = {})
    skills = Skill.all
    skills = skills.where(name: filters[:name]) if filters[:name].present?
    skills.order(created_at: :desc)
  end

  def self.get(id)
    Skill.find(id)
  end

  def self.create(params)
    Skill.create!(
      name: params[:name],
      description: params[:description],
      prompt: params[:prompt],
      input_schema: params[:input_schema] || {},
      output_schema: params[:output_schema] || {},
      version: params[:version] || 1,
      metadata: params[:metadata] || {}
    )
  end

  def self.execute(id, input = {})
    skill = Skill.find(id)
    execution = skill.executions.new(input: input, status: "running", executed_at: Time.current)
    simulated_output = execute_skill(skill, input)
    execution.update!(output: simulated_output, status: "completed")
    execution
  rescue ActiveRecord::RecordNotFound
    raise
  rescue StandardError => e
    execution&.update!(status: "failed", error_message: e.message) if execution&.persisted?
    raise
  end

  private

  def self.execute_skill(skill, input)
    {
      result: "Executed #{skill.name} with input: #{input.to_json}",
      skill_version: skill.version,
      executed_at: Time.current.iso8601
    }
  end
end
