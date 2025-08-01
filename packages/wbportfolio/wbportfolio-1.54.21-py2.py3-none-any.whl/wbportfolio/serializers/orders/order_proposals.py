from decimal import Decimal

from django.contrib.messages import warning
from django.core.exceptions import ValidationError
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.serializers import DefaultFromView

from wbportfolio.models import OrderProposal, Portfolio, RebalancingModel

from .. import PortfolioRepresentationSerializer, RebalancingModelRepresentationSerializer


class OrderProposalRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:orderproposal-detail")

    class Meta:
        model = OrderProposal
        fields = ("id", "trade_date", "status", "_detail")


class OrderProposalModelSerializer(wb_serializers.ModelSerializer):
    rebalancing_model = wb_serializers.PrimaryKeyRelatedField(queryset=RebalancingModel.objects.all(), required=False)
    _rebalancing_model = RebalancingModelRepresentationSerializer(source="rebalancing_model")
    target_portfolio = wb_serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(), write_only=True, required=False
    )
    _target_portfolio = PortfolioRepresentationSerializer(source="target_portfolio")
    total_cash_weight = wb_serializers.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=5,
        write_only=True,
        required=False,
        precision=4,
        percent=True,
        label="Target Cash",
        help_text="Enter the desired percentage for the cash component. The remaining percentage (100% minus this value) will be allocated to total target weighting. Default is 0%.",
    )

    trade_date = wb_serializers.DateField(
        read_only=lambda view: not view.new_mode, default=DefaultFromView("default_trade_date")
    )

    def create(self, validated_data):
        target_portfolio = validated_data.pop("target_portfolio", None)
        total_cash_weight = validated_data.pop("total_cash_weight", Decimal("0.0"))
        rebalancing_model = validated_data.get("rebalancing_model", None)
        if request := self.context.get("request"):
            validated_data["creator"] = request.user.profile
        obj = super().create(validated_data)

        target_portfolio_dto = None
        if target_portfolio:
            target_portfolio_dto = target_portfolio._build_dto(obj.trade_date)
        elif rebalancing_model:
            target_portfolio_dto = rebalancing_model.get_target_portfolio(
                obj.portfolio, obj.trade_date, obj.last_effective_date
            )

        try:
            obj.reset_orders(
                target_portfolio=target_portfolio_dto, total_target_weight=Decimal("1.0") - total_cash_weight
            )
        except ValidationError as e:
            if request := self.context.get("request"):
                warning(request, str(e), extra_tags="auto_close=0")
        return obj

    @wb_serializers.register_only_instance_resource()
    def additional_resources(self, instance, request, user, **kwargs):
        res = {}
        if instance.status == OrderProposal.Status.APPROVED:
            res["replay"] = reverse("wbportfolio:orderproposal-replay", args=[instance.id], request=request)
        if instance.status == OrderProposal.Status.DRAFT:
            res["reset"] = reverse("wbportfolio:orderproposal-reset", args=[instance.id], request=request)
            res["normalize"] = reverse("wbportfolio:orderproposal-normalize", args=[instance.id], request=request)
            res["deleteall"] = reverse("wbportfolio:orderproposal-deleteall", args=[instance.id], request=request)
        res["orders"] = reverse(
            "wbportfolio:orderproposal-order-list",
            args=[instance.id],
            request=request,
        )
        return res

    class Meta:
        model = OrderProposal
        only_fsm_transition_on_instance = True
        fields = (
            "id",
            "trade_date",
            "total_cash_weight",
            "comment",
            "status",
            "min_order_value",
            "portfolio",
            "_rebalancing_model",
            "rebalancing_model",
            "target_portfolio",
            "_target_portfolio",
            "_additional_resources",
        )


class ReadOnlyOrderProposalModelSerializer(OrderProposalModelSerializer):
    class Meta(OrderProposalModelSerializer.Meta):
        read_only_fields = OrderProposalModelSerializer.Meta.fields
