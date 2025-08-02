from typing import Type, Any, Dict, List, Optional, Union
from motor.motor_asyncio import AsyncIOMotorDatabase
from beanie import Document
from ..schema.base_schema import FilterSchema, SortDirection, SortSchema
from ..schema.base_schema import ( 
    BaseChartSchema, 
    ChartAggregation, 
    TopNSpec, 
    AggregationBinningSpec
)
from ..schema.charts_schema import ( 
    AggregationType,
    IntValueOptions, 
    DateValueOptions, 
    StrValueOptions,
    BinningSpec,
    NumberChartDataSchema,
    BarChartDataSchema,
    ColumnChartDataSchema,
    LineChartDataSchema,
    PieChartDataSchema,
    ScatterChartDataSchema,
    CandlestickChartDataSchema,
    TableChartDataSchema
)
from ..schema.base_schema import AggregationSpec

from abs_nosql_repository_core.repository.base_repository import BaseRepository


class BaseChartRepository(BaseRepository):
    def __init__(self, document: Type[Document] = None, db: AsyncIOMotorDatabase = None, **kwargs):
        super().__init__(document=document, db=db, **kwargs)

    def _get_sort_order(self, sort_order: List[SortSchema], for_aggregation: bool = False) -> Union[List[tuple], Dict[str, int]]:
        """Generate sort for MongoDB queries or aggregation pipelines"""
        if not sort_order:
            return [("created_at", -1)] if not for_aggregation else {"created_at": -1}
        
        if for_aggregation:
            return {
                s.field.replace('.', '_') if isinstance(s.field, str) else str(s.field).replace('.', '_'): 
                (1 if s.direction == SortDirection.ASC else -1)
                for s in sort_order
            }
        else:
            return [
                (s.field, 1 if s.direction == SortDirection.ASC else -1)
                for s in sort_order
            ]


    async def get_chart_data_pipeline(self, chart_schema: BaseChartSchema) -> Any:
        """
        Main entry point: Validates and processes the chart schema, builds the pipeline, and fetches data.
        """
        pipeline = []
        if getattr(chart_schema, "filters", None):
            filter_condition = self._build_query_filter(chart_schema.filters)
            if filter_condition:
                pipeline.append({"$match": filter_condition})

        chart_type = getattr(chart_schema, "chart_type", None)
        chart_type_str = chart_type.value.lower() if hasattr(chart_type, 'value') else str(chart_type).lower() if chart_type else None
        
        if chart_type_str in ["pie", "donut", "gauge"]:
            chart_data = self.build_pie_chart_aggregation(chart_schema.data)
        elif chart_type_str == "number":
            chart_data = self.build_number_chart_aggregation(chart_schema.data)
        elif chart_type_str in ["line", "area"]:
            chart_data = self.build_line_chart_aggregation(chart_schema.data)
        elif chart_type_str in ["bar", "stacked_bar", "stacked_bar_100"]:
            chart_data = self.build_bar_chart_aggregation(chart_schema.data)
        elif chart_type_str in ["column", "stacked_column", "stacked_column_100"]:
            chart_data = self.build_column_chart_aggregation(chart_schema.data)
        elif chart_type_str == "scatter":
            chart_data = self.build_scatter_chart_aggregation(chart_schema.data)
        elif chart_type_str == "candlestick":
            chart_data = self.build_candlestick_chart_aggregation(chart_schema.data)
        elif chart_type_str == "table":
            chart_data = self.build_table_chart_aggregation(chart_schema.data)
        else:
            chart_data = self.build_number_chart_aggregation(chart_schema.data)
        
        pipeline.extend(chart_data['pipeline'])
        
        aggregation = chart_data.get('chart_agg', None)
        if aggregation is not None:
            aggregation_stages = self._build_aggregation_stage(
                aggregation, 
                chart_type_str
            )
            pipeline += aggregation_stages

        post_group_project = chart_data.get('post_group_project', None)
        if post_group_project:
            if isinstance(post_group_project, list):
                pipeline.extend(post_group_project)
            else:
                pipeline.append(post_group_project)

        print("pipeline",pipeline)
        data = {
            "pipeline" : pipeline,
            "chart_type": chart_type_str,
            "group_alias": chart_data.get('group_alias', None)
        }
        
        return data
    

    def _build_query_filter(
        self, filters: Optional[FilterSchema]= None, collection_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Build MongoDB filter from ListFilter"""
        if filters:
            if hasattr(filters, "model_dump"):
                filter = filters.model_dump(exclude_none=True)
            else:
                filter = {k: v for k, v in filters.items() if v is not None}
        else:
            filter = {}

        base_filter = (
            self._build_filter_condition(filter, collection_name, is_expr=False)
            if filters
            else None
        )

        return base_filter
    

    def _build_label_stage(self, aggregation: ChartAggregation) -> dict | None:
        """Return a $addFields stage for a user-friendly label based on binning or group_by."""
        add_fields = {}
        
        if aggregation.binning_specs and len(aggregation.binning_specs) > 0:
            binning_spec = aggregation.binning_specs[0]
            bin_value = binning_spec.bin_value
            alias = binning_spec.alias or binning_spec.field
            if isinstance(bin_value, DateValueOptions):
                granularity = bin_value.granularity or "month"
                granularity_to_format = {
                    "year": "%Y",
                    "month": "%Y-%m",
                    "week": "%G-W%V",
                    "day": "%Y-%m-%d",
                    "hour": "%Y-%m-%dT%H",
                    "minute": "%Y-%m-%dT%H:%M",
                    "second": "%Y-%m-%dT%H:%M:%S",
                    "periodic month": "%m",
                    "periodic day": "%d",
                    "periodic week": "%V",
                    "periodic hour": "%H",
                    "periodic minute": "%M",
                    "periodic second": "%S",
                }
                format_str = granularity_to_format.get(granularity, "%Y-%m-%d")
                add_fields["label"] = {"$dateToString": {"format": format_str, "date": f"$_id.{alias}"}}
            else:
                add_fields["label"] = f"$_id.{alias}"
        else:
            if aggregation.group_by and len(aggregation.group_by) > 0:
                group_field = aggregation.group_by[0]
                add_fields["label"] = f"$_id.{group_field}"
        
        if aggregation.group_by and len(aggregation.group_by) > 1:
            series_field = aggregation.group_by[1]
            add_fields["type"] = {"$toString": f"$_id.{series_field}"}
        
        return {"$addFields": add_fields} if add_fields else None

    def _build_aggregation_stage(self, aggregation: ChartAggregation, chart_type: str) -> List[Dict[str, Any]]:
        """Build MongoDB aggregation stage from ChartAggregation"""

        pipeline = []
        
        if getattr(aggregation, "binning_specs", None):
            binning_stages = self._build_binning_stage(aggregation.binning_specs)
            pipeline.extend(binning_stages)

        group_stage = self._build_group_stage(aggregation)
        if "$group" in group_stage and "count" not in group_stage["$group"]:
            group_stage["$group"]["count"] = {"$sum": 1}

        pipeline.append(group_stage)

        label_stage = self._build_label_stage(aggregation) if chart_type != "table" else None
        if label_stage:
            pipeline.append(label_stage)

        if getattr(aggregation, "sort_by", None):
            sort_by = self._get_sort_order(aggregation.sort_by, for_aggregation=True)
        else:
            sort_by = {"label": 1}

        if sort_by:
            pipeline.append({"$sort": sort_by})

        if getattr(aggregation, "top_n", None):
            pipeline.extend(self.build_top_n_pipeline(aggregation.top_n, aggregation.aggregation_fields))

        if getattr(aggregation, "aggregation_fields", None) and chart_type != "table":
            project_fields = {"_id": 1, "count": 1,"label": 1}
            values_array = []
            
            for agg in aggregation.aggregation_fields:
                alias = agg.alias
                agg_type = agg.type.lower()
                field_name = agg.field
                
                sanitized_alias = alias.replace('.', '_') if isinstance(alias, str) else str(alias).replace('.', '_')

                if agg_type == "distinct":
                    values_array.append({
                        "$cond": {
                            "if": {"$isArray": f"${sanitized_alias}"},
                            "then": {
                                "field": field_name, 
                                "type": agg_type, 
                                "value": {"$size": f"${sanitized_alias}"},
                                "alias": alias
                            },
                            "else": {
                                "field": field_name, 
                                "type": agg_type, 
                                "value": 0,
                                "alias": alias
                            }
                        }
                    })
                else:
                    values_array.append({
                        "field": field_name,
                        "type": agg_type,
                        "value": f"${sanitized_alias}",
                        "alias": alias
                    })
            
            project_fields["values"] = values_array
            pipeline.append({"$project": project_fields})

        return pipeline


    def _build_group_stage(self, group_agg: ChartAggregation) -> Dict[str, Any]:
        effective_group_by = group_agg.group_by
        if group_agg.binning_specs:
            effective_group_by = self._update_group_by_with_binning(
                group_agg.group_by, 
                group_agg.binning_specs
            )

        _id = (
            {field: f"${field}" for field in effective_group_by}
            if effective_group_by
            else None
        )
        group_stage = {"_id": _id}

        if group_agg.aggregation_fields:
            for agg in group_agg.aggregation_fields:
                agg_type = agg.type.lower()
                field = agg.field
                alias = agg.alias

                sanitized_alias = alias.replace('.', '_') if isinstance(alias, str) else str(alias).replace('.', '_')
                
                if agg_type == "count":
                    group_stage[sanitized_alias] = {"$sum": 1}
                elif agg_type == "distinct":
                    group_stage[sanitized_alias] = {"$addToSet": f"${field}"}
                elif agg_type == "std_dev":
                    group_stage[sanitized_alias] = {"$stdDevPop": f"${field}"}
                elif agg_type == "variance":
                    raise NotImplementedError("Variance is not directly supported by MongoDB aggregation.")
                elif agg_type == "first":
                    group_stage[sanitized_alias] = {"$first": f"${field}"}
                elif agg_type == "last":
                    group_stage[sanitized_alias] = {"$last": f"${field}"}
                elif agg_type in AggregationType:
                    group_stage[sanitized_alias] = {f"${agg_type}": f"${field}"}
                else:
                    raise ValueError(f"Unsupported aggregation type: {agg_type}")
        return {"$group": group_stage}
        

    @staticmethod
    def build_top_n_pipeline(top_n: TopNSpec, aggregation_fields: List[AggregationSpec] = None) -> List[Dict[str, Any]]:
        """Build pipeline for top N results, with optional 'Others' grouping."""
        pipeline = []
        
        if not getattr(top_n, 'others', False):
            pipeline.append({"$limit": top_n.value})
            return pipeline
        
        others_group = {
            "_id": "Others",
            "count": {"$sum": "$count"}
        }

        others_pipeline = [{"$skip": top_n.value}]
        
        if aggregation_fields:
            for agg_spec in aggregation_fields:
                agg_type = agg_spec.type.lower()
                alias = agg_spec.alias
                
                if agg_type == "sum":
                    others_group[alias] = {"$sum": f"${alias}"}
                elif agg_type == "avg":
                    others_group[alias] = {"$avg": f"${alias}"}
                elif agg_type == "count":
                    others_group[alias] = {"$sum": f"${alias}"}
                elif agg_type == "max":
                    others_group[alias] = {"$max": f"${alias}"}
                elif agg_type == "min":
                    others_group[alias] = {"$min": f"${alias}"}
                elif agg_type == "distinct":
                    others_pipeline.append({"$unwind": f"${alias}"})
                    others_group[alias] = {"$addToSet": f"${alias}"}
                elif agg_type == "std_dev":
                    others_group[alias] = {"$stdDevPop": f"${alias}"}
                elif agg_type == "first":
                    others_group[alias] = {"$first": f"${alias}"}
                elif agg_type == "last":
                    others_group[alias] = {"$last": f"${alias}"}
                else:
                    others_group[alias] = {"$sum": f"${alias}"}
        
        others_pipeline.append({"$group": others_group})
        others_pipeline.append({"$addFields": {"label": "Others"}})
        pipeline = [
            {"$facet": {
                "topN": [
                    {"$limit": top_n.value}
                ],
                "others": others_pipeline
            }},
            {"$project": {
                "all": {"$concatArrays": ["$topN", "$others"]}
            }},
            {"$unwind": "$all"},
            {"$replaceRoot": {"newRoot": "$all"}}
        ]
        
        return pipeline
        

    def _build_binning_stage(self, binning_specs: List[AggregationBinningSpec]) -> List[Dict[str, Any]]:
        """Build MongoDB aggregation stages for binning operations"""
        if not binning_specs:
            return []
        
        stages = []
        add_fields_stage = {}
        
        for binning_spec in binning_specs:
            if not binning_spec.enabled or not binning_spec.bin_value:
                continue
            
            field = binning_spec.field
            alias = binning_spec.alias or field
            bin_value = binning_spec.bin_value
            
            if isinstance(bin_value, IntValueOptions):
                binning_expr = self._build_numeric_binning_expr(field, bin_value)
            elif isinstance(bin_value, DateValueOptions):
                binning_expr = self._build_date_binning_expr(field, bin_value)
            elif isinstance(bin_value, StrValueOptions):
                binning_expr = self._build_string_binning_expr(field, bin_value)
            else:
                continue
            
            add_fields_stage[alias] = binning_expr
        
        if add_fields_stage:
            stages.append({"$addFields": add_fields_stage})

        return stages
    
    def _build_numeric_binning_expr(self, field: str, int_options: IntValueOptions) -> Dict[str, Any]:
        """Build MongoDB expression for numeric binning"""
        bin_size = int_options.value or 10
        
        return {
            "$multiply": [
                {"$floor": {"$divide": [f"${field}", bin_size]}},
                bin_size
            ]
        }
    
    def _build_date_binning_expr(self, field: str, date_options: DateValueOptions) -> Dict[str, Any]:
        """Build safe date binning expression with $convert to ensure type correctness"""
        granularity = date_options.granularity or "day"
        timezone = date_options.timezone or "UTC"

        date_field = f"${field}"

        return {
            "$cond": {
                "if": {
                    "$and": [
                        { "$ne": [date_field, None] },
                        { "$ne": [date_field, ""] }
                    ]
                },
                "then": {
                    "$dateTrunc": {
                        "date": {
                            "$convert": {
                                "input": date_field,
                                "to": "date",
                                "onError": None,
                                "onNull": None
                            }
                        },
                        "unit": granularity.replace("periodic ", ""),
                        "timezone": timezone
                    }
                },
                "else": None
            }
        }


    
    def _build_string_binning_expr(self, field: str, str_options: StrValueOptions) -> Dict[str, Any]:
        """Build MongoDB expression for string value grouping"""
        conditions = []        
        for group in str_options.groups:
            condition = {
                "case": {"$in": [f"${field}", group.values]},
                "then": group.label
            }
            conditions.append(condition)
        
        return {
            "$switch": {
                "branches": conditions,
                "default": "Other"
            }
        }
    
    def _update_group_by_with_binning(self, group_by: List[str], binning_specs: List[BinningSpec]) -> List[str]:
        """Update group_by fields to use binned field aliases where applicable"""
        if not binning_specs:
            return group_by

        field_mapping = {}
        for binning_spec in binning_specs:
            if binning_spec.enabled:
                alias = binning_spec.alias or binning_spec.field
                field_mapping[binning_spec.field] = alias
        
        updated_group_by = []
        for field in group_by:
            updated_field = field_mapping.get(field, field)
            updated_group_by.append(updated_field)
        
        return updated_group_by
    

    def build_unwind_and_group_path(self, field_path: str):
        """
        Creates a pipeline that handles any combination of arrays/objects dynamically.
        """
        path_parts = field_path.split('.')
        pipeline = []
        
        if len(path_parts) > 1:
            for i, part in enumerate(path_parts[:-1]):
                current_path = '.'.join(path_parts[:i+1])
                
                pipeline.extend([
                    {
                        "$addFields": {
                            f"_normalized_{i}": {
                                "$switch": {
                                    "branches": [
                                        {
                                            "case": {"$eq": [{"$type": f"${current_path}"}, "array"]},
                                            "then": f"${current_path}"
                                        },
                                        {
                                            "case": {"$eq": [{"$type": f"${current_path}"}, "object"]},
                                            "then": [f"${current_path}"]
                                        }
                                    ],
                                    "default": []
                                }
                            }
                        }
                    },
                    {
                        "$unwind": {
                            "path": f"$_normalized_{i}",
                            "preserveNullAndEmptyArrays": True
                        }
                    },
                    {
                        "$addFields": {
                            current_path: f"$_normalized_{i}"
                        }
                    }
                ])
            
            cleanup_fields = [f"_normalized_{i}" for i in range(len(path_parts) - 1)]
            pipeline.append({"$unset": cleanup_fields})
        
        return pipeline, field_path
    
    def create_top_n_spec(self, agg_alias: str, top_n_config) -> TopNSpec | None:
        """
        Create a TopNSpec for ChartAggregation given the aggregation alias and top_n config.
        """
        if not top_n_config:
            return None
        return TopNSpec(
            field=agg_alias,
            value=getattr(top_n_config, 'value', None) or getattr(top_n_config, 'n', None) or 10,
            others=getattr(top_n_config, 'others', False)
        )
    
    def build_number_chart_aggregation(self, data: NumberChartDataSchema ):
        """
        Build ChartAggregation for NumberChartDataSchema.
        Handles nested arrays/objects generically:
        - Uses build_unwind_and_group_path to add $unwind for every array in the type path.
        - The final group_by path is the full nested path (usually empty for number chart, but supports advanced cases).
        - Returns: (pipeline_stages, chart_agg, post_group_project)
        """
        number = data.number
        pipeline, group_by_field = self.build_unwind_and_group_path(number.field)
            
        agg_spec = AggregationSpec(
            field=number.field, 
            type=AggregationType(number.aggregation),
            alias=getattr(number, "label", number.field) or number.field
        )
        chart_agg = ChartAggregation(
            group_by=[],
            aggregation_fields=[agg_spec]
        )
        post_group_project = None
        
        number_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": chart_agg,
            "post_group_project": post_group_project,
            "group_alias": getattr(number, "label", number.field) or number.field
        }
        return number_chart_data

    def build_pie_chart_aggregation(self, data:PieChartDataSchema):
        """
        Build ChartAggregation for PieChartDataSchema.
        Handles nested arrays/objects generically:
        - Uses build_unwind_and_group_path to add $unwind for every array in the type path.
        - The final group_by path is the full nested path.
        - Returns: (pipeline_stages, chart_agg, post_group_project)
        """
        group_by = data.group_by
        value = data.value

        pipeline, group_by_field = self.build_unwind_and_group_path(group_by.field)

        binning_specs = [{**group_by.binning.model_dump(), "field": group_by.field, "alias": group_by.label}] if getattr(group_by, 'binning', None) and getattr(group_by.binning, 'enabled', False) else None
        agg_spec = AggregationSpec(
            field=value.field,
            type=AggregationType(value.aggregation),
            alias=getattr(value, "label", value.field) or value.field
        )
        sort_by = [ 
            { 
                "field": agg_spec.alias, 
                "direction": (group_by.sort_by.value if group_by.sort_by else None) or SortDirection.DESC
                }
        ]
        top_n = self.create_top_n_spec(agg_spec.alias,group_by.top_n) if getattr(group_by, 'top_n', None) else None

        chart_agg = ChartAggregation(
            group_by=[group_by_field],
            aggregation_fields=[agg_spec],
            binning_specs=binning_specs,
            sort_by=sort_by,
            top_n=top_n
        )
        post_group_project = None
        
        pie_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": chart_agg,
            "post_group_project": post_group_project,
            "group_alias": getattr(group_by, "label", group_by.field) or group_by.field
        }
        return pie_chart_data

    def build_line_chart_aggregation(self, data:LineChartDataSchema):
        """
        Build ChartAggregation for LineChartDataSchema.
        - Uses build_unwind_and_group_path for x.field (and group_by.field if present)
        - Supports binning on x and group_by
        - Supports multiple y fields, each with its own aggregation
        - group_by can only be used when there's exactly one y field (ignored if multiple y)
        - Returns: (pipeline_stages, chart_agg, post_group_project)
        """
        x = data.x
        y_list = data.y
        group_by = getattr(data, 'group_by', None)
        
        if group_by and len(y_list) > 1:
            group_by = None 
        
        pipeline, group_by_field = self.build_unwind_and_group_path(x.field)
        group_by_list = [group_by_field]
        binning_specs = [ {**x.binning.model_dump(), "field": x.field,"alias": x.label} ] if getattr(x, 'binning', None) and getattr(x.binning, 'enabled', False) else None
        
        if group_by:
            group_by_pipeline, group_by_group_by_field = self.build_unwind_and_group_path(group_by.field)
            pipeline += group_by_pipeline
            group_by_list.append(group_by_group_by_field)
            if getattr(group_by, 'binning', None) and getattr(group_by.binning, 'enabled', False):
                if binning_specs:
                    binning_specs.append({**group_by.binning.model_dump(), "field": group_by.field, "alias": group_by.label})
                else:
                    binning_specs = [{**group_by.binning.model_dump(), "field": group_by.field, "alias": group_by.label}]

        agg_specs = []
        for y in y_list:
            agg_type = y.aggregation or 'sum'
            
            agg_specs.append(
                AggregationSpec(
                    field=y.field,
                    type=AggregationType(agg_type),
                    alias=getattr(y, 'label', y.field) or y.field
                )
            )

        sort_by = None
        if x.field_type in ['date', 'datetime', 'timestamp',"int","number"]:
            sort_by = [{ "field": "label", "direction": (x.sort_by.value if x.sort_by else None) or SortDirection.ASC}]
        elif getattr(x, 'sort_by', None):
            sort_by = []
            for agg_spec in agg_specs:
                sort_by.append({
                    "field": agg_spec.alias, 
                    "direction": (x.sort_by.value if x.sort_by else None) or SortDirection.ASC
                })

        top_n = self.create_top_n_spec(group_by_field, x.top_n) if getattr(x, 'top_n', None) else None
        
        chart_agg = ChartAggregation(
            group_by=group_by_list,
            aggregation_fields=agg_specs,
            binning_specs=binning_specs,
            sort_by=sort_by,
            top_n=top_n
        )
        post_group_project = None

        line_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": chart_agg,
            "post_group_project": post_group_project,
            "group_alias": getattr(x, "label", x.field) or x.field
        }
        return line_chart_data

    def build_bar_chart_aggregation(self, data:BarChartDataSchema):
        """
        Build ChartAggregation for BarChartDataSchema.
        - Uses build_unwind_and_group_path for y.field (and group_by.field if present)
        - Supports binning on y and group_by
        - Supports multiple x fields, each with its own aggregation
        - group_by can only be used when there's exactly one x field (ignored if multiple x)
        - Returns: (pipeline_stages, chart_agg, post_group_project)
        """
        x_list = data.x
        y = data.y
        group_by = getattr(data, 'group_by', None)
        if group_by and len(x_list) > 1:
            group_by = None
        
        pipeline, group_by_field = self.build_unwind_and_group_path(y.field)
        group_by_list = [group_by_field]
        
        binning_specs = [{**y.binning.model_dump(), "field": y.field, "alias": y.label}] if getattr(y, 'binning', None) and getattr(y.binning, 'enabled', False) else None
        
        if group_by:
            group_by_pipeline, group_by_group_by_field = self.build_unwind_and_group_path(group_by.field)
            pipeline += group_by_pipeline
            group_by_list.append(group_by_group_by_field)
            
            if getattr(group_by, 'binning', None) and getattr(group_by.binning, 'enabled', False):
                if binning_specs:
                    binning_specs.append({**group_by.binning.model_dump(), "field": group_by.field, "alias": group_by.label})
                else:
                    binning_specs = [{**group_by.binning.model_dump(), "field": group_by.field, "alias": group_by.label}]

        agg_specs = []
        for x in x_list:
            agg_type = x.aggregation or 'sum'
            
            agg_specs.append(
                AggregationSpec(
                    field=x.field,
                    type=AggregationType(agg_type),
                    alias=getattr(x, 'label', x.field) or x.field
                )
            )

        sort_by = None
        if y.field_type in ['date', 'datetime', 'timestamp', "int", "number"]:
            sort_by = [{"field": "label", "direction": (y.sort_by.value if y.sort_by else None) or SortDirection.ASC}]
        elif getattr(y, 'sort_by', None):
            sort_by = []
            for agg_spec in agg_specs:
                sort_by.append({
                    "field": agg_spec.alias,
                    "direction": (y.sort_by.value if y.sort_by else None) or SortDirection.ASC
                })
        top_n = self.create_top_n_spec(group_by_field, y.top_n) if getattr(y, 'top_n', None) else None
        
        chart_agg = ChartAggregation(
            group_by=group_by_list,
            aggregation_fields=agg_specs,
            binning_specs=binning_specs,
            sort_by=sort_by,
            top_n=top_n
        )
        post_group_project = None
        
        bar_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": chart_agg,
            "post_group_project": post_group_project,
            "group_alias": getattr(y, "label", y.field) or y.field
        }
        return bar_chart_data

    def build_column_chart_aggregation(self, data:ColumnChartDataSchema):
        """
        Build ChartAggregation for ColumnChartDataSchema.
        - Uses build_unwind_and_group_path for x.field (and group_by.field if present)
        - Supports binning on x and group_by
        - Supports multiple y fields, each with its own aggregation
        - group_by can only be used when there's exactly one y field (ignored if multiple y)
        - Returns: (pipeline_stages, chart_agg, post_group_project)
        """
        x = data.x
        y_list = data.y
        group_by = getattr(data, 'group_by', None)
        
        if group_by and len(y_list) > 1:
            group_by = None
        
        pipeline, group_by_field = self.build_unwind_and_group_path(x.field)
        group_by_list = [group_by_field]
        binning_specs = [ {**x.binning.model_dump(), "field": x.field,"alias": x.label} ] if getattr(x, 'binning', None) and getattr(x.binning, 'enabled', False) else None
        
        if group_by:
            group_by_pipeline, group_by_group_by_field = self.build_unwind_and_group_path(group_by.field)
            pipeline += group_by_pipeline
            group_by_list.append(group_by_group_by_field)
            if getattr(group_by, 'binning', None) and getattr(group_by.binning, 'enabled', False):
                if binning_specs:
                    binning_specs.append({**group_by.binning.model_dump(), "field": group_by.field, "alias": group_by.label})
                else:
                    binning_specs = [{**group_by.binning.model_dump(), "field": group_by.field, "alias": group_by.label}]

        agg_specs = []
        for y in y_list:
            agg_type = y.aggregation or 'sum'
            
            agg_specs.append(
                AggregationSpec(
                    field=y.field,
                    type=AggregationType(agg_type),
                    alias=getattr(y, 'label', y.field) or y.field
                )
            )

        sort_by = None
        if x.field_type in ['date', 'datetime', 'timestamp', "int", "number"]:
            sort_by = [{"field": "label", "direction": (x.sort_by.value if x.sort_by else None) or SortDirection.ASC}]
        elif getattr(x, 'sort_by', None):
            sort_by = []
            for agg_spec in agg_specs:
                sort_by.append({
                    "field": agg_spec.alias,
                    "direction": (x.sort_by.value if x.sort_by else None) or SortDirection.ASC
                })

        top_n = self.create_top_n_spec(group_by_field, x.top_n) if getattr(x, 'top_n', None) else None
        
        chart_agg = ChartAggregation(
            group_by=group_by_list,
            aggregation_fields=agg_specs,
            binning_specs=binning_specs,
            sort_by=sort_by,
            top_n=top_n
        )
        post_group_project = None
        
        column_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": chart_agg,
            "post_group_project": post_group_project,
            "group_alias": getattr(x, "label", x.field) or x.field
        }
        return column_chart_data

    def build_scatter_chart_aggregation(self, data:ScatterChartDataSchema):
        """
        Build pipeline for ScatterChartDataSchema.
        - Scatter plots show individual data points without aggregation
        - Uses build_unwind_and_group_path for x.field and y.field
        - No binning, no aggregation, no series
        - Returns: (pipeline_stages, None, post_group_project)
        """
        x = data.x
        y = data.y
        
        pipeline, x_group_by_field = self.build_unwind_and_group_path(x.field)
        
        y_pipeline, y_group_by_field = self.build_unwind_and_group_path(y.field)
        pipeline += y_pipeline
        
        post_group_project = {
            "$project": {
                "x": f"${x.field}",
                "y": f"${y.field}",
                "label_x": getattr(x, 'label', x.field),
                "label_y": getattr(y, 'label', y.field)
            }
        }
        
        scatter_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": None,
            "post_group_project": post_group_project,
            "group_alias": None
        }
        return scatter_chart_data

    def build_candlestick_chart_aggregation(self, data:CandlestickChartDataSchema):
        """
        Build ChartAggregation for CandlestickChartDataSchema.
        - Uses build_unwind_and_group_path for x.field
        - Only int and date fields are allowed for x
        - Only numeric values (number/int/float) are allowed for high, low, open, close
        - Default sort is ASC by x
        - When top_n is present, others is forced to False
        - Returns: (pipeline_stages, chart_agg, post_group_project)
        """
        x = data.x
        high = data.high
        low = data.low
        open_field = data.open
        close = data.close
        
        x_field_type = getattr(x, 'field_type', None) or 'string'
        if x_field_type not in ['int', 'number', 'datetime', 'date', 'timestamp']:
            raise ValueError(f"X field type '{x_field_type}' is not allowed for candlestick charts. Only int, number, date, datetime, or timestamp are allowed.")
        
        numeric_fields = [high, low, open_field, close]
        for field in numeric_fields:
            field_type = getattr(field, 'field_type', None) or 'string'
            if field_type not in ['int', 'number', 'float', 'decimal']:
                raise ValueError(f"Field type '{field_type}' is not allowed for candlestick numeric fields. Only int, number, float, or decimal are allowed.")
        
        pipeline, group_by_field = self.build_unwind_and_group_path(x.field)
        group_by = [group_by_field]
        
        binning_specs = [{**x.binning.model_dump(), "field": x.field, "alias": x.label}] if getattr(x, 'binning', None) and getattr(x.binning, 'enabled', False) else None
        
        agg_specs = []

        high_alias = f"High"
        low_alias = f"Low"
        open_alias = f"Open"
        close_alias = f"Close"
        
        agg_specs.append(
            AggregationSpec(
                field=high.field,
                type=AggregationType('max'),
                alias=high_alias
            )
        )
        
        agg_specs.append(
            AggregationSpec(
                field=low.field,
                type=AggregationType('min'),
                alias=low_alias
            )
        )
        
        agg_specs.append(
            AggregationSpec(
                field=open_field.field,
                type=AggregationType('first'),
                alias=open_alias
            )
        )
        
        agg_specs.append(
            AggregationSpec(
                field=close.field,
                type=AggregationType('last'),
                alias=close_alias
            )
        )

        sort_by = None
        if getattr(x, 'sort_by', None):
            sort_by = [{"field": "label", "direction": x.sort_by.value or SortDirection.ASC}]
        else:
            sort_by = [{"field": "label", "direction": SortDirection.ASC}]
        
        top_n = None
        if getattr(x, 'top_n', None):
            top_n_config = x.top_n
            top_n = TopNSpec(
                field=group_by_field,
                value=getattr(top_n_config, 'value', None) or getattr(top_n_config, 'n', None) or 10,
                others=False
            )
        
        chart_agg = ChartAggregation(
            group_by=group_by,
            aggregation_fields=agg_specs,
            binning_specs=binning_specs,
            sort_by=sort_by,
            top_n=top_n
        )

        post_group_project = None
        
        candlestick_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": chart_agg,
            "post_group_project": post_group_project,
            "group_alias": getattr(x, "label", x.field) or x.field
        }
        return candlestick_chart_data

    

    def build_table_chart_aggregation(self, data:TableChartDataSchema):
        """
        Build ChartAggregation for TableChartDataSchema.
        - Supports multiple groups and values.
        - If limit is set, applies $limit at the end of the pipeline.
        - Returns: (pipeline_stages, chart_agg, post_group_project)
        """
        groups = data.groups
        values = data.values
        limit = getattr(data, 'limit', None)

        group_by_fields = []
        pipeline = []
        binning_specs = []
        project_fields = {}
        for group in groups:
            unwind_stages, group_by_field = self.build_unwind_and_group_path(group.field)
            project_fields[group.label or group.field] = { "field": group_by_field, "type": group.field_type }
            pipeline += unwind_stages
            group_by_fields.append(group_by_field)
            if getattr(group, 'binning', None) and getattr(group.binning, 'enabled', False):
                binning_spec = {**group.binning.model_dump(), "field": group.field, "alias": group.label}
                binning_specs.append(binning_spec)
                project_fields[group.label or group.field]["binning"] = binning_spec

        agg_specs = []
        for value in values:
            unwind_stages, group_by_field = self.build_unwind_and_group_path(value.field)
            pipeline += unwind_stages
            agg_type = value.aggregation or 'sum'
            agg_specs.append(
                AggregationSpec(
                    field=value.field,
                    type=AggregationType(agg_type),
                    alias=getattr(value, 'label', value.field) or value.field
                )
            )

        chart_agg = ChartAggregation(
            group_by=group_by_fields,
            aggregation_fields=agg_specs,
            binning_specs=binning_specs if binning_specs else None,
            sort_by=None,
            top_n=None
        )        
        post_group_project = self._build_table_groups_project(project_fields, agg_specs, limit)

        table_chart_data = { 
            "pipeline": pipeline,
            "chart_agg": chart_agg,
            "post_group_project": post_group_project,
            "group_alias": None
        }
        return table_chart_data

    def _build_table_groups_project(self, project_fields, agg_specs, limit):
        """
        Build a post-group projection for table charts that creates a 'groups' object
        with all group fields and their values, processing binning if applicable.
        """
        project_stages = []
        
        projection_fields = {
            "_id": 1,
            "count": 1
        }
        
        values_array = []
        for agg in agg_specs:
            alias = agg.alias
            agg_type = agg.type.lower()
            field_name = agg.field
            
            sanitized_alias = alias.replace('.', '_') if isinstance(alias, str) else str(alias).replace('.', '_')
            # projection_fields[sanitized_alias] = f"${sanitized_alias}"

            if agg_type == "distinct":
                values_array.append({
                    "$cond": {
                        "if": {"$isArray": f"${sanitized_alias}"},
                        "then": {
                            "field": field_name, 
                            "type": agg_type, 
                            "value": {"$size": f"${sanitized_alias}"},
                            "alias": alias
                        },
                        "else": {
                            "field": field_name, 
                            "type": agg_type, 
                            "value": 0,
                            "alias": alias
                        }
                    }
                })
            else:

                values_array.append({
                    "field": field_name,
                    "type": agg_type,
                    "value": f"${sanitized_alias}",
                    "alias": alias
                })
        
        groups_object = {}
        
        for label, field_info in project_fields.items():
            field_name = field_info['field']
            field_type = field_info['type']
            
            if 'binning' in field_info:
                binning_spec = field_info['binning']
                bin_value = binning_spec.get('bin_value')
                
                if hasattr(bin_value, 'granularity') and bin_value.granularity:
                    granularity = bin_value.granularity
                    timezone = getattr(bin_value, 'timezone', 'UTC')
                    granularity_to_format = {
                        "year": "%Y",
                        "month": "%Y-%m",
                        "week": "%G-W%V",
                        "day": "%Y-%m-%d",
                    }
                    format_str = granularity_to_format.get(granularity, "%Y-%m-%d")
                    groups_object[label] = {
                        "$dateToString": {
                            "format": format_str, 
                            "date": f"$_id.{label}",
                            "timezone": timezone
                        }
                    }
                else:
                    groups_object[label] = f"$_id.{label}"
            else:
                groups_object[label] = f"$_id.{field_name}"
        
        projection_fields["groups"] = groups_object
        projection_fields["values"] = values_array
        project_stages.append({"$project": projection_fields})
        
        # Add a total row at the end
        project_stages.append({
            "$facet": {
                "data": [{"$match": {}}],
                "totals": [
                    {"$group": {
                        "_id": "total",
                        "count": {"$sum": "$count"}
                    }},
                    {"$project": {
                        "_id": "total",
                        "count": 1,
                        "groups": {"total": "Total"},
                        "values": [
                            {
                                "field": "_id",
                                "type": "count", 
                                "value": "$count",
                                "alias": "calls"
                            }
                        ]
                    }}
                ]
            }
        })
        
        # Unwind and combine data with totals
        project_stages.append({
            "$project": {
                "combined": {
                    "$concatArrays": ["$data", "$totals"]
                }
            }
        })
        project_stages.append({"$unwind": "$combined"})
        project_stages.append({"$replaceRoot": {"newRoot": "$combined"}})
        
        if limit is not None:
            project_stages.append({"$limit": limit})
        
        print("project_stages",project_stages)
        return project_stages if len(project_stages) > 1 else project_stages[0] if project_stages else None


