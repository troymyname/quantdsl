from eventsourcing.domain.model.events import subscribe, unsubscribe

from quantdsl.domain.model.call_dependencies import CallDependenciesRepository
from quantdsl.domain.model.call_link import CallLinkRepository
from quantdsl.domain.model.call_requirement import CallRequirementRepository
from quantdsl.domain.model.call_result import CallResultRepository
from quantdsl.domain.model.contract_valuation import ContractValuation, ContractValuationRepository
from quantdsl.domain.model.market_simulation import MarketSimulationRepository, MarketSimulation
from quantdsl.domain.model.simulated_price import SimulatedPriceRepository
from quantdsl.domain.services.contract_valuations import evaluate_contract_in_series


class EvaluationSubscriber(object):

    def __init__(self, contract_valuation_repo, call_link_repo, call_dependencies_repo, call_requirement_repo,
                 call_result_repo, simulated_price_repo, market_simulation_repo):
        assert isinstance(contract_valuation_repo, ContractValuationRepository), contract_valuation_repo
        assert isinstance(call_link_repo, CallLinkRepository), call_link_repo
        assert isinstance(call_dependencies_repo, CallDependenciesRepository), call_dependencies_repo
        assert isinstance(call_requirement_repo, CallRequirementRepository), call_requirement_repo
        assert isinstance(call_result_repo, CallResultRepository), call_result_repo
        assert isinstance(simulated_price_repo, SimulatedPriceRepository), simulated_price_repo
        assert isinstance(market_simulation_repo, MarketSimulationRepository), market_simulation_repo
        self.contract_valuation_repo = contract_valuation_repo
        self.call_link_repo = call_link_repo
        self.call_dependencies_repo = call_dependencies_repo
        self.call_requirement_repo = call_requirement_repo
        self.call_result_repo = call_result_repo
        self.simulated_price_repo = simulated_price_repo
        self.market_simulation_repo = market_simulation_repo
        subscribe(self.contract_valuation_created, self.generate_contract_valuation)

    def close(self):
        unsubscribe(self.contract_valuation_created, self.generate_contract_valuation)

    def contract_valuation_created(self, event):
        return isinstance(event, ContractValuation.Created)

    def generate_contract_valuation(self, event):
        assert isinstance(event, ContractValuation.Created)
        contract_valuation = self.contract_valuation_repo[event.entity_id]
        assert isinstance(contract_valuation, ContractValuation), contract_valuation
        market_simulation = self.market_simulation_repo[contract_valuation.market_simulation_id]
        assert isinstance(market_simulation, MarketSimulation), market_simulation
        evaluate_contract_in_series(
            market_simulation,
            contract_valuation.dependency_graph_id,
            self.simulated_price_repo,
            self.call_requirement_repo,
            self.call_dependencies_repo,
            self.call_link_repo,
            self.call_result_repo)
