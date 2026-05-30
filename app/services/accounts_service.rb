class AccountsService
  def self.create(params)
    Account.create!(
      name: params[:name],
      balance: params[:balance] || 0.0
    )
  end

  def self.get_balance(id)
    Account.find(id)
  end
end
