<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>工单详情 - {{ order?.order_no }}</h2>
      <div>
        <el-button @click="goBack">返回列表</el-button>
      </div>
    </div>

    <template v-if="order">
      <!-- ==================== 操作栏 ==================== -->
      <el-card shadow="hover" class="status-card">
        <div class="status-card-body">
          <div class="status-info">
            <el-tag type="primary" size="large">{{ order.status_name }}</el-tag>
            <span v-if="order.parts_total > 0" style="margin-left: 12px; color: #909399; font-size: 14px;">
              备件: {{ order.parts_outbound_count }}/{{ order.parts_total }} 已出库
            </span>
          </div>
          <div class="status-actions">
            <el-button
              v-if="order.status === 0 && perm('work_order:settle') && !isFromPartsOutbound"
              type="success"
              @click="handleSubmitPayment"
            >
              提交收款
            </el-button>
            <el-button
              v-if="order.status === 1 && perm('work_order:status')"
              type="warning"
              @click="handleRevertToRepair"
            >
              退回在修
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- ==================== 基本信息 ==================== -->
      <el-card shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>基本信息</span>
            <el-button v-if="canEditBase && !isFromPartsOutbound" type="primary" size="small" @click="showEditBase = true">编辑</el-button>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="工单号">{{ order.order_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(order.status)">{{ order.status_name }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="维修类别">{{ order.repair_category || order.service_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ order.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ order.customer_phone }}</el-descriptions-item>
          <el-descriptions-item label="车牌号">{{ order.plate_number }}</el-descriptions-item>
          <el-descriptions-item label="品牌车型">{{ order.vehicle_brand }} {{ order.vehicle_model }}</el-descriptions-item>
          <el-descriptions-item label="进厂里程">{{ order.mileage }} km</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(order.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="操作人">{{ order.creator_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="故障描述" :span="3">{{ order.fault_description }}</el-descriptions-item>
          <el-descriptions-item label="维修建议" :span="3">{{ order.repair_suggestion || '暂无' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- ==================== 费用信息（状态 >= 2 显示） ==================== -->
      <el-card v-if="showCost" shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>费用信息</span>
            <el-button v-if="canEditCost" type="primary" size="small" @click="showEditCost = true">编辑费用</el-button>
          </div>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="工时费">¥{{ Number(order.labor_cost || 0).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="配件金额">¥{{ Number(order.parts_cost || 0).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="自费金额">¥{{ chargeTypeAmounts['自费'].toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="索赔金额">¥{{ chargeTypeAmounts['索赔'].toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="保险金额">¥{{ chargeTypeAmounts['保险'].toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="优惠金额">¥{{ Number(order.discount_amount || 0).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="总金额">
            <span style="font-size: 18px; font-weight: bold; color: #f56c6c;">¥{{ Number(order.total_amount || 0).toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="已收金额">¥{{ actualReceived.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="索赔厂家">
            <el-select v-if="order.status === 0 && !isFromPaymentList" v-model="order.claim_manufacturer" placeholder="选择" size="small" clearable filterable allow-create style="width: 160px;" @change="saveOrderField('claim_manufacturer', $event)">
              <el-option v-for="m in manufacturerList" :key="m.id" :label="m.name" :value="m.name" />
            </el-select>
            <span v-else>{{ order.claim_manufacturer || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="保险公司">
            <el-select v-if="order.status === 0 && !isFromPaymentList" v-model="order.insurance_company" placeholder="选择" size="small" clearable filterable allow-create style="width: 160px;" @change="saveOrderField('insurance_company', $event)">
              <el-option v-for="c in insuranceList" :key="c.id" :label="c.name" :value="c.name" />
            </el-select>
            <span v-else>{{ order.insurance_company || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="收款状态">
            <el-tag :type="paymentStatusType">{{ paymentStatusText }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- ==================== 维修项目（状态 >= 0 始终显示） ==================== -->
      <el-card shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>维修项目</span>
            <el-button
              v-if="canEditItems"
              type="primary"
              size="small"
              @click="showAddItem = true"
            >添加维修项目</el-button>
          </div>
        </template>
        <el-table :data="order.repair_items || []" stripe>
          <el-table-column prop="item_code" label="项目编码" width="120" />
          <el-table-column prop="item_name" label="项目名称" />
          <el-table-column prop="labor_hours" label="工时" width="80" />
          <el-table-column prop="labor_price" label="单价" width="100">
            <template #default="{ row }">¥{{ Number(row.labor_price).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="labor_amount" label="金额" width="100">
            <template #default="{ row }">¥{{ Number(row.labor_amount).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="discount_rate" label="折扣率" width="100">
            <template #default="{ row }">
              <el-input-number v-if="canEditItems" v-model="row.discount_rate" :min="0" :max="1" :precision="2" :step="0.05" size="small" controls-position="right" style="width:80px;" @change="saveItemField(row, 'discount_rate', $event)" />
              <span v-else>{{ (Number(row.discount_rate || 1) * 100).toFixed(0) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="actual_amount" label="实收金额" width="100">
            <template #default="{ row }">
              <span style="font-weight:500; color:#67c23a;">¥{{ (Number(row.labor_amount || 0) * Number(row.discount_rate || 1)).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="charge_type" label="收费类型" width="110">
            <template #default="{ row }">
              <el-select v-if="canEditItems" v-model="row.charge_type" placeholder="选择" size="small" clearable style="width:100%;" @change="saveItemField(row, 'charge_type', $event)">
                <el-option v-for="ft in feeTypeList" :key="ft.id" :label="ft.name" :value="ft.name" />
              </el-select>
              <span v-else>{{ row.charge_type || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="repair_category" label="维修类别" width="110">
            <template #default="{ row }">
              <el-select v-if="canEditItems" v-model="row.repair_category" placeholder="选择" size="small" clearable style="width:100%;" @change="saveItemField(row, 'repair_category', $event)">
                <el-option v-for="rc in repairCategoryList" :key="rc.id" :label="rc.name" :value="rc.name" />
              </el-select>
              <span v-else>{{ row.repair_category || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="technician_name" label="技师" width="140">
            <template #default="{ row }">
              <el-select
                v-if="canEditItems"
                v-model="row.technician_id"
                placeholder="选择技师"
                size="small"
                clearable
                style="width: 100%;"
                @change="(val) => handleTechnicianChange(row, val)"
              >
                <el-option
                  v-for="t in technicianList"
                  :key="t.id"
                  :label="t.name"
                  :value="t.id"
                />
              </el-select>
              <span v-else>{{ row.technician_name || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="canEditItems" label="操作" width="80" align="center">
            <template #default="{ row }">
              <el-popconfirm title="确定删除此维修项目？" @confirm="handleDeleteItem(row)">
                <template #reference>
                  <el-button type="danger" size="small" link>删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!order.repair_items || order.repair_items.length === 0" description="暂无维修项目" :image-size="60" />
      </el-card>

      <!-- ==================== 备件信息（状态 >= 2 显示） ==================== -->
      <el-card v-if="showParts" shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>配件信息</span>
            <el-button
              v-if="canEditParts"
              type="primary"
              size="small"
              @click="openAddPart"
            >
              添加配件
            </el-button>
          </div>
        </template>

        <el-table :data="orderParts" stripe>
          <el-table-column prop="part_no" label="配件编号" width="130" />
          <el-table-column prop="part_name" label="配件名称" min-width="140">
            <template #default="{ row }">
              {{ row.part_name }}
              <span v-if="row.part_brand || row.part_specification" style="color: #999; font-size: 12px;">({{ [row.part_brand, row.part_specification].filter(Boolean).join(' ') }})</span>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" align="center">
            <template #default="{ row }">
              <el-input-number
                v-if="canEditParts"
                v-model="row.quantity"
                :min="0"
                :max="999"
                size="small"
                controls-position="right"
                style="width: 90px;"
                @change="(val) => handlePartQtyChange(row, val)"
              />
              <span v-else>{{ row.quantity }} {{ row.part_unit }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.unit_price).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="total_price" label="小计" width="110" align="right">
            <template #default="{ row }">
              <span style="font-weight: 500;">¥{{ Number(row.total_price).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <!-- 成本字段：需要时取消注释即可显示
          <el-table-column prop="cost_price_no_tax" label="不含税成本单价" width="120" align="right">
            <template #default="{ row }">¥{{ Number(row.cost_price_no_tax || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="cost_total_no_tax" label="不含税成本总价" width="120" align="right">
            <template #default="{ row }">¥{{ Number(row.cost_total_no_tax || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="cost_price_with_tax" label="含税成本单价" width="120" align="right">
            <template #default="{ row }">¥{{ Number(row.cost_price_with_tax || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="cost_total_with_tax" label="含税成本总价" width="120" align="right">
            <template #default="{ row }">¥{{ Number(row.cost_total_with_tax || 0).toFixed(2) }}</template>
          </el-table-column>
          -->
          <el-table-column prop="discount_rate" label="折扣率" width="100" align="center">
            <template #default="{ row }">
              <el-input-number v-if="canEditParts" v-model="row.discount_rate" :min="0" :max="1" :precision="2" :step="0.05" size="small" controls-position="right" style="width:80px;" @change="savePartDiscount(row, $event)" />
              <span v-else>{{ (Number(row.discount_rate || 1) * 100).toFixed(0) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="actual_amount" label="实收金额" width="110" align="right">
            <template #default="{ row }">
              <span style="font-weight:500; color:#67c23a;">¥{{ (Number(row.total_price || 0) * Number(row.discount_rate || 1)).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="charge_type" label="收费类型" width="110">
            <template #default="{ row }">
              <el-select v-if="canEditParts" v-model="row.charge_type" placeholder="选择" size="small" clearable style="width:100%;" @change="savePartField(row, 'charge_type', $event)">
                <el-option v-for="ft in feeTypeList" :key="ft.id" :label="ft.name" :value="ft.name" />
              </el-select>
              <span v-else>{{ row.charge_type || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="repair_category" label="维修类别" width="110">
            <template #default="{ row }">
              <el-select v-if="canEditParts" v-model="row.repair_category" placeholder="选择" size="small" clearable style="width:100%;" @change="savePartField(row, 'repair_category', $event)">
                <el-option v-for="rc in repairCategoryList" :key="rc.id" :label="rc.name" :value="rc.name" />
              </el-select>
              <span v-else>{{ row.repair_category || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="出库状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.outbound_status === 1" type="success" size="small">已出库</el-tag>
              <el-tag v-else type="info" size="small">未出库</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
          <el-table-column label="操作" width="120" align="center" v-if="canEditParts">
            <template #default="{ row }">
              <div style="display: flex; justify-content: center; gap: 8px;">
                <div style="width: 36px; text-align: center;">
                  <el-popconfirm :title="row.outbound_status === 1 ? '确定删除此配件？库存将回退！' : '确定删除此配件？'" width="280" @confirm="handleRemovePart(row)">
                    <template #reference>
                      <el-button v-if="isFromPartsOutbound || row.outbound_status !== 1" type="danger" size="small" link>删除</el-button>
                      <span v-else>&nbsp;</span>
                    </template>
                  </el-popconfirm>
                </div>
                <div style="width: 36px; text-align: center;">
                  <el-button v-if="isFromPartsOutbound && row.outbound_status !== 1" type="success" link size="small" @click="handlePartOutbound(row)">出库</el-button>
                  <span v-else>&nbsp;</span>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 备件汇总 -->
        <div v-if="orderParts.length > 0" style="margin-top: 12px; text-align: right; padding-right: 20px;">
          <span style="font-size: 14px; color: #606266;">备件合计：</span>
          <span style="font-size: 16px; font-weight: bold; color: #f56c6c;">
            ¥{{ partsTotal.toFixed(2) }}
          </span>
        </div>
        <el-empty v-else description="暂无备件信息" :image-size="60" />
      </el-card>

      <!-- ==================== 财务收款（收款状态显示） ==================== -->
      <el-card v-if="showPayment" shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>财务收款</span>
            <el-button v-if="!isFromPartsOutbound" type="primary" size="small" @click="openAddPayment">收款</el-button>
          </div>
        </template>
        <!-- 收款汇总 -->
        <el-descriptions :column="4" border style="margin-bottom: 16px;">
          <el-descriptions-item label="应收金额">
            <span style="font-weight: bold; color: #f56c6c;">¥{{ Number(order.total_amount || 0).toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="已收金额">
            <span style="font-weight: bold; color: #67c23a;">¥{{ actualReceived.toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="未收金额">
            <span style="font-weight: bold;" :style="{ color: unpaidAmount > 0 ? '#f56c6c' : '#67c23a' }">
              ¥{{ unpaidAmount.toFixed(2) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="收款状态">
            <el-tag :type="paymentStatusType" size="small">{{ paymentStatusText }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <!-- 收款记录列表 -->
        <el-table :data="orderPayments" stripe size="small">
          <el-table-column prop="payment_no" label="收款编号" width="160">
            <template #default="{ row }">
              <el-link type="primary" @click="router.push(`/finance/payments/${row.id}`)">{{ row.payment_no }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="120" align="right">
            <template #default="{ row }">
              <span :style="{ fontWeight: 500, color: Number(row.amount) < 0 ? '#f56c6c' : '#67c23a' }">¥{{ Number(row.amount).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="payment_type" label="类型" width="80" align="center">
            <template #default="{ row }">{{ { repair: '收款', deposit: '定金', refund: '退款', other: '其他' }[row.payment_type] || row.payment_type || '-' }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="{ 0: 'warning', 1: 'success', 2: 'danger' }[row.status] || 'info'" size="small">{{ { 0: '待确认', 1: '已确认', 2: '已退款' }[row.status] || '未知' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="payment_method" label="收款方式" width="100">
            <template #default="{ row }">{{ { cash: '现金', wechat: '微信', alipay: '支付宝', bank: '银行卡' }[row.payment_method] || row.payment_method || '-' }}</template>
          </el-table-column>
          <el-table-column prop="payer_name" label="付款人" width="100" />
          <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
        <el-empty v-if="orderPayments.length === 0" description="暂无收款记录" :image-size="60" />
      </el-card>

      <!-- ==================== 开票信息（收款状态显示） ==================== -->
      <el-card v-if="showPayment" shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>开票信息</span>
            <el-button v-if="!isFromPartsOutbound" type="primary" size="small" @click="openAddInvoice">新增开票</el-button>
          </div>
        </template>
        <el-table :data="orderInvoices" stripe size="small">
          <el-table-column prop="invoice_no" label="发票号" width="180" />
          <el-table-column prop="title" label="发票抬头" min-width="150" />
          <el-table-column prop="invoice_type" label="类型" width="80">
            <template #default="{ row }">{{ row.invoice_type === 'normal' ? '普通' : '专用' }}</template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="120" align="right">
            <template #default="{ row }">
              <span style="font-weight: 500;">¥{{ Number(row.amount).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="tax_amount" label="税额" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.tax_amount).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="['info', 'success', 'danger'][row.status]" size="small">
                {{ ['待开票', '已开票', '已作废'][row.status] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="creator_name" label="操作人" width="100" align="center">
            <template #default="{ row }">{{ row.creator_name || '-' }}</template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ row }">
              <el-button v-if="row.status === 0" type="success" link size="small" @click="handleIssueInvoice(row)">开具</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="orderInvoices.length === 0" description="暂无开票记录" :image-size="60" />
      </el-card>

      <!-- ==================== 状态流转记录（始终显示） ==================== -->
      <el-card shadow="hover">
        <template #header>操作记录</template>
        <el-table :data="order.flow_logs || []" stripe size="small">
          <el-table-column prop="operator_no" label="工号" width="120" />
          <el-table-column prop="operator_name" label="姓名" width="100" />
          <el-table-column prop="operator_dept" label="部门" width="120" />
          <el-table-column prop="operation" label="操作" min-width="150">
            <template #default="{ row }">
              {{ formatOperation(row.operation) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="操作时间" width="170">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>

    <!-- ==================== 编辑基本信息对话框 ==================== -->
    <el-dialog v-model="showEditBase" title="编辑基本信息" width="600px">
      <el-form :model="baseForm" label-width="100px">
        <el-form-item label="维修类别">
          <el-select v-model="baseForm.service_type" placeholder="请选择" style="width: 100%;">
            <el-option v-for="rc in repairCategoryList" :key="rc.id" :label="rc.name" :value="rc.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="进厂里程">
          <el-input-number v-model="baseForm.mileage" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="故障描述">
          <el-input v-model="baseForm.fault_description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="维修建议">
          <el-input v-model="baseForm.repair_suggestion" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="baseForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditBase = false">取消</el-button>
        <el-button type="primary" :loading="baseSaving" @click="handleSaveBase">保存</el-button>
      </template>
    </el-dialog>

    <!-- ==================== 编辑费用对话框 ==================== -->
    <el-dialog v-model="showEditCost" title="编辑费用" width="500px">
      <el-form :model="costForm" label-width="100px">
        <el-form-item label="折扣率(%)">
          <el-input-number v-model="costForm.discount_rate" :min="0" :max="100" :precision="0" :step="5" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditCost = false">取消</el-button>
        <el-button type="primary" :loading="costSaving" @click="handleSaveCost">保存</el-button>
      </template>
    </el-dialog>

    <!-- ==================== 收款对话框 ==================== -->
    <el-dialog v-model="showAddPayment" title="收款" width="500px">
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="未收金额">
          <span style="font-weight: bold; color: #f56c6c;">¥{{ unpaidAmount.toFixed(2) }}</span>
        </el-form-item>
        <el-form-item label="收款金额" required>
          <el-input-number v-model="paymentForm.amount" :min="0.01" :max="unpaidAmount" :precision="2" :step="100" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="收款方式" required>
          <el-select v-model="paymentForm.payment_method" placeholder="请选择" style="width: 100%;">
            <el-option v-for="ct in chargeTypeList" :key="ct.id" :label="ct.name" :value="ct.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款人" required>
          <el-input v-model="paymentForm.payer_name" :placeholder="order?.customer_name || ''" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="paymentForm.remark" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPayment = false">取消</el-button>
        <el-button type="primary" :loading="paymentSaving" @click="handleAddPayment">确认收款</el-button>
      </template>
    </el-dialog>

    <!-- ==================== 新增开票对话框 ==================== -->
    <el-dialog v-model="showAddInvoice" title="新增开票" width="500px" @close="resetInvoiceForm">
      <el-form :model="invoiceForm" label-width="80px">
        <el-form-item label="抬头" required>
          <el-input v-model="invoiceForm.title" placeholder="请输入发票抬头" />
        </el-form-item>
        <el-form-item label="税号">
          <el-input v-model="invoiceForm.tax_no" placeholder="请输入税号" />
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="invoiceForm.amount" :min="0.01" :precision="2" :step="100" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="税额">
          <el-input-number v-model="invoiceForm.tax_amount" :min="0" :precision="2" :step="10" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="发票类型">
          <el-select v-model="invoiceForm.invoice_type" style="width: 100%;">
            <el-option label="普通发票" value="normal" />
            <el-option label="专用发票" value="special" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddInvoice = false">取消</el-button>
        <el-button type="primary" :loading="invoiceSaving" @click="handleAddInvoice">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- ==================== 添加维修项目对话框 ==================== -->
    <el-dialog v-model="showAddItem" title="添加维修项目" width="700px" @open="loadItemTemplates">
      <div style="margin-bottom: 12px;">
        <el-input v-model="templateKeyword" placeholder="搜索项目名称/编码" clearable style="width: 240px;" @input="searchTemplates" />
      </div>
      <el-table
        :data="filteredTemplates"
        stripe
        highlight-current-row
        v-loading="templatesLoading"
        max-height="400"
        @row-click="onTemplateSelect"
        style="cursor: pointer;"
      >
        <el-table-column prop="item_code" label="项目编码" width="120" />
        <el-table-column prop="item_name" label="项目名称" min-width="140" />
        <el-table-column prop="labor_hours" label="工时" width="80" align="center">
          <template #default="{ row }">{{ row.labor_hours }}h</template>
        </el-table-column>
        <el-table-column prop="labor_price" label="单价" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.labor_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="labor_amount" label="工时费" width="100" align="right">
          <template #default="{ row }">
            <span style="font-weight: 500;">¥{{ Number(row.labor_amount).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="120" show-overflow-tooltip />
      </el-table>

      <!-- 已选项目预览 -->
      <div v-if="selectedTemplate" style="margin-top: 16px; padding: 12px; background: #f5f7fa; border-radius: 6px;">
        <div style="font-weight: 500; margin-bottom: 8px;">已选项目：{{ selectedTemplate.item_name }}</div>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="工时" label-width="50px" style="margin-bottom: 0;">
              <el-input-number v-model="itemForm.labor_hours" :min="0" :precision="1" :step="0.5" size="small" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" label-width="50px" style="margin-bottom: 0;">
              <el-input-number v-model="itemForm.labor_price" :min="0" :precision="2" :step="10" size="small" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注" label-width="50px" style="margin-bottom: 0;">
              <el-input v-model="itemForm.remark" placeholder="选填" size="small" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <template #footer>
        <el-button @click="showAddItem = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedTemplate" @click="handleAddItem">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- ==================== 添加配件对话框 ==================== -->
    <el-dialog v-model="showAddPart" title="添加配件" width="950px" @open="loadPartsList">
      <div style="margin-bottom: 12px;">
        <el-input v-model="partKeyword" placeholder="搜索配件名称/编号" clearable style="width: 240px;" @input="onPartSearchInput" @clear="loadPartsList" />
      </div>
      <el-table
        ref="partsTableRef"
        :data="partsList"
        stripe
        highlight-current-row
        v-loading="partsLoading"
        max-height="350"
        @current-change="onPartCurrentChange"
        style="cursor: pointer;"
      >
        <el-table-column prop="part_no" label="配件编码" width="120" />
        <el-table-column prop="name" label="配件名称" min-width="140" />
        <el-table-column prop="brand" label="品牌" width="100" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格" width="100" show-overflow-tooltip />
        <el-table-column prop="unit" label="单位" width="60" align="center" />
        <el-table-column prop="stock_quantity" label="库存" width="80" align="center" />
        <el-table-column prop="selling_price" label="销售单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.selling_price).toFixed(2) }}</template>
        </el-table-column>
      </el-table>

      <!-- 已选配件预览 -->
      <div v-if="selectedPart" style="margin-top: 16px; padding: 12px; background: #f5f7fa; border-radius: 6px;">
        <div style="font-weight: 500; margin-bottom: 8px;">已选配件：{{ selectedPart.part_no }} - {{ selectedPart.name }}</div>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="数量" label-width="50px" style="margin-bottom: 0;">
              <el-input-number v-model="partForm.quantity" :min="1" :max="Math.max(selectedPartStock, 1)" size="small" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="单价" label-width="50px" style="margin-bottom: 0;">
              <el-input-number v-model="partForm.unit_price" :min="selectedPartDefaultPrice" :precision="2" :step="10" size="small" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="备注" label-width="50px" style="margin-bottom: 0;">
              <el-input v-model="partForm.remark" placeholder="选填" size="small" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <template #footer>
        <el-button @click="showAddPart = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedPart" :loading="partSubmitting" @click="handleAddPart">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const order = ref(null)
const loading = ref(false)

// ==================== 权限检查 ====================
const perm = (p) => userStore.hasPermission(p)

// 返回上一个页面
function goBack() {
  router.back()
}

// ==================== 状态配置 ====================
const statusNames = ['在修', '结算']

// 是否从配件出库步骤进入
const isFromPartsOutbound = computed(() => (route.query.from || '') === 'parts-outbound')

// ==================== 计算属性：根据状态控制显示/编辑 ====================
const currentStatus = computed(() => order.value?.status ?? -1)
const isPartsOutboundDone = computed(() => {
  if (!orderParts.value || orderParts.value.length === 0) return false
  return orderParts.value.every(p => p.outbound_status === 1)
})
const hasParts = computed(() => orderParts.value && orderParts.value.length > 0)

// 是否从收款列表进入（只读模式）
const isFromPaymentList = computed(() => (route.query.from || '').startsWith('payment'))

// 基本信息：始终可编辑
const canEditBase = computed(() => !isFromPaymentList.value && perm('work_order:update'))

// 维修项目：可增删
const canEditItems = computed(() => !isFromPaymentList.value && !isFromPartsOutbound.value && perm('work_order:repair'))

// 备件区域：始终显示
const showParts = computed(() => true)

// 备件可操作
const canEditParts = computed(() => !isFromPaymentList.value && perm('work_order:parts'))

// 费用区域：始终显示
const showCost = computed(() => true)

// 费用可编辑：暂不开放
const canEditCost = computed(() => false)

// 财务收款：始终显示（在修可直接提交收款）
const showPayment = computed(() => perm('work_order:settle'))

// 未收金额
// 根据收款记录动态计算实际已收金额（已支付 + 退款负值）
const actualReceived = computed(() => {
  return orderPayments.value
    .filter(p => p.status === 1 || p.status === 2)
    .reduce((sum, p) => sum + Number(p.amount || 0), 0)
})

const unpaidAmount = computed(() => {
  const total = Number(order.value?.total_amount || 0)
  return Math.max(0, total - actualReceived.value)
})

const paymentStatusText = computed(() => {
  const total = Number(order.value?.total_amount || 0)
  const received = actualReceived.value
  if (total <= 0) return '无需收款'
  if (received <= 0) return '未收款'
  if (received > total) return '超收'
  if (received >= total) return '收清'
  return '部分收款'
})

const paymentStatusType = computed(() => {
  const total = Number(order.value?.total_amount || 0)
  const received = actualReceived.value
  if (total <= 0) return 'info'
  if (received <= 0) return 'danger'
  if (received > total) return 'warning'
  if (received >= total) return 'success'
  return ''
})

// 按收费类型汇总实收金额（工时+备件）
const chargeTypeAmounts = computed(() => {
  const items = order.value?.repair_items || []
  const parts = order.value?.order_parts || []
  const result = { '自费': 0, '索赔': 0, '保险': 0 }
  for (const item of items) {
    const type = item.charge_type || '自费'
    if (type in result) {
      result[type] += Number(item.labor_amount || 0) * Number(item.discount_rate || 1)
    }
  }
  for (const p of parts) {
    const type = p.charge_type || '自费'
    if (type in result) {
      result[type] += Number(p.total_price || 0) * Number(p.discount_rate || 1)
    }
  }
  return result
})

// 提交收款（在修提交待确认收款单）
const submitPaymentLoading = ref(false)
async function handleSubmitPayment() {
  // 校验是否存在保险/索赔项目（不依赖金额）
  const items = order.value?.repair_items || []
  const parts = order.value?.order_parts || []
  const hasInsurance = items.some(i => i.charge_type === '保险') || parts.some(p => p.charge_type === '保险')
  const hasClaim = items.some(i => i.charge_type === '索赔') || parts.some(p => p.charge_type === '索赔')
  if (hasInsurance && !order.value?.insurance_company) {
    return ElMessage.warning('本单有保险，必须填写具体保险公司！')
  }
  if (hasClaim && !order.value?.claim_manufacturer) {
    return ElMessage.warning('本单有索赔，必须填写具体索赔厂家！')
  }
  // 检查备件出库状态
  const partsStatus = order.value?.parts_outbound_status
  if (partsStatus === 'none_outbound' || partsStatus === 'partial') {
    return ElMessage.warning('有配件未出库，请全部出库后再提交！')
  }
  const unpaid = Number(order.value.total_amount || 0) - actualReceived.value
  try {
    await ElMessageBox.confirm(
      `本工单将变更为"结算"状态！`,
      '提交收款',
      { type: 'info', confirmButtonText: '确认提交', cancelButtonText: '取消' }
    )
  } catch { return }
  submitPaymentLoading.value = true
  try {
    await request.post(`/work-orders/${route.params.id}/submit-payment`)
    ElMessage.success('工单已变更为结算，收款单待财务确认')
    router.back()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    submitPaymentLoading.value = false
  }
}

// 退回在修
const revertLoading = ref(false)
async function handleRevertToRepair() {
  try {
    await ElMessageBox.confirm('确定将工单退回"在修"状态？已生成的收款单不受影响。', '退回在修', { type: 'warning' })
  } catch { return }
  revertLoading.value = true
  try {
    await request.put(`/work-orders/${route.params.id}/status`, { status: 0, remark: '退回在修' })
    ElMessage.success('工单已退回在修状态')
    router.back()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    revertLoading.value = false
  }
}

// ==================== 编辑基本信息 ====================
const showEditBase = ref(false)
const baseSaving = ref(false)
const baseForm = reactive({
  service_type: '',
  mileage: 0,
  fault_description: '',
  repair_suggestion: '',
  remark: ''
})

function openEditBase() {
  if (!order.value) return
  baseForm.service_type = order.value.service_type || (repairCategoryList.value[0]?.name || '保养')
  baseForm.mileage = order.value.mileage || 0
  baseForm.fault_description = order.value.fault_description || ''
  baseForm.repair_suggestion = order.value.repair_suggestion || ''
  baseForm.remark = order.value.remark || ''
  showEditBase.value = true
}

async function handleSaveBase() {
  baseSaving.value = true
  try {
    await request.put(`/work-orders/${route.params.id}`, baseForm)
    ElMessage.success('基本信息已更新')
    showEditBase.value = false
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    baseSaving.value = false
  }
}

// ==================== 编辑费用 ====================
const showEditCost = ref(false)
const costSaving = ref(false)
const costForm = reactive({
  other_cost: 0,
  discount_rate: 100
})

function openEditCost() {
  if (!order.value) return
  costForm.other_cost = Number(order.value.other_cost || 0)
  costForm.discount_rate = Number((order.value.discount_rate || 1) * 100)
  showEditCost.value = true
}

async function saveOrderField(field, value) {
  try {
    await request.put(`/work-orders/${order.value.id}/field`, { [field]: value })
  } catch (e) { console.error('保存失败', e) }
}

async function handleSaveCost() {
  costSaving.value = true
  try {
    await request.put(`/work-orders/${route.params.id}/discount`, {
      discount_rate: costForm.discount_rate / 100,
      other_cost: costForm.other_cost
    })
    ElMessage.success('费用信息已更新')
    showEditCost.value = false
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    costSaving.value = false
  }
}

// ==================== 维修项目模板 ====================
const technicianList = ref([])
const manufacturerList = ref([])
const insuranceList = ref([])
const chargeTypeList = ref([])
const feeTypeList = ref([])
const repairCategoryList = ref([])

async function loadTechnicianList() {
  try {
    const res = await request.get('/technicians/all')
    technicianList.value = res.data || []
  } catch (e) { console.error('加载技师列表失败', e) }
}

async function loadDictList() {
  try {
    const [mRes, iRes, ctRes, ftRes, rcRes] = await Promise.all([
      request.get('/dict/manufacturers'),
      request.get('/dict/insurances'),
      request.get('/system/dict-items', { params: { type: 'charge_type' } }),
      request.get('/system/dict-items', { params: { type: 'fee_type' } }),
      request.get('/system/dict-items', { params: { type: 'repair_category' } })
    ])
    manufacturerList.value = (mRes.data || []).filter(i => i.status === 1)
    insuranceList.value = (iRes.data || []).filter(i => i.status === 1)
    chargeTypeList.value = (ctRes.data || []).filter(i => i.status === 1)
    feeTypeList.value = (ftRes.data || []).filter(i => i.status === 1)
    repairCategoryList.value = (rcRes.data || []).filter(i => i.status === 1)
  } catch (e) { console.error('加载字典数据失败', e) }
}

// 记录用户手动修改过技师的项目ID
const manualEditedItems = new Set()
const manualEditedFields = new Set() // 记录手动修改过的项目ID+字段

async function saveItemField(row, field, value) {
  try {
    await request.put(`/work-orders/${order.value.id}/items/${row.id}`, { [field]: value })
    // 记录手动修改
    manualEditedFields.add(`${row.id}:${field}`)
    // 如果修改的是第一个项目的收费类型或维修类别，自动同步其他未手动修改的项目
    const items = order.value.repair_items || []
    if (items.length > 1 && row.id === items[0].id && (field === 'charge_type' || field === 'repair_category')) {
      const syncItems = items.filter(item => item.id !== row.id && !manualEditedFields.has(`${item.id}:${field}`))
      for (const item of syncItems) {
        try {
          await request.put(`/work-orders/${order.value.id}/items/${item.id}`, { [field]: value })
          item[field] = value
        } catch (e) { console.error('同步失败', e) }
      }
    }
    loadOrder()
  } catch (e) { console.error('保存失败', e) }
}

async function handleTechnicianChange(row, val) {
  const tech = technicianList.value.find(t => t.id === val)
  const technician_name = tech ? tech.name : ''
  try {
    await request.put(`/work-orders/${order.value.id}/items/${row.id}`, {
      technician_id: val || null,
      technician_name
    })
    row.technician_name = technician_name
    // 记录为手动修改
    manualEditedItems.add(row.id)
    // 自动同步其他未手动修改的项目
    const items = order.value.repair_items || []
    const syncItems = items.filter(item => item.id !== row.id && !manualEditedItems.has(item.id))
    for (const item of syncItems) {
      try {
        await request.put(`/work-orders/${order.value.id}/items/${item.id}`, {
          technician_id: val || null,
          technician_name
        })
        item.technician_id = val || null
        item.technician_name = technician_name
      } catch (e) { console.error('同步技师失败', e) }
    }
    ElMessage.success('技师分配成功')
    loadOrder()
  } catch (e) {
    ElMessage.error('技师分配失败')
  }
}

const showAddItem = ref(false)
const itemForm = reactive({ item_name: '', item_code: '', category: '', labor_hours: 0, labor_price: 0, remark: '', charge_type: '自费', repair_category: '保养' })
const templatesLoading = ref(false)
const allTemplates = ref([])
const filteredTemplates = ref([])
const selectedTemplate = ref(null)
const templateKeyword = ref('')

async function loadItemTemplates() {
  templatesLoading.value = true
  templateKeyword.value = ''
  selectedTemplate.value = null
  Object.assign(itemForm, { item_name: '', item_code: '', category: '', labor_hours: 0, labor_price: 0, remark: '', charge_type: '自费', repair_category: '保养' })
  try {
    const res = await request.get('/repair-items/all')
    allTemplates.value = res.data || []
    filteredTemplates.value = allTemplates.value
  } catch (e) {
    console.error('加载维修项目模板失败', e)
  } finally { templatesLoading.value = false }
}

function searchTemplates() {
  const kw = templateKeyword.value.toLowerCase()
  if (!kw) {
    filteredTemplates.value = allTemplates.value
  } else {
    filteredTemplates.value = allTemplates.value.filter(t =>
      (t.item_name && t.item_name.toLowerCase().includes(kw)) ||
      (t.item_code && t.item_code.toLowerCase().includes(kw))
    )
  }
}

function onTemplateSelect(row) {
  selectedTemplate.value = row
  itemForm.item_name = row.item_name
  itemForm.item_code = row.item_code || ''
  itemForm.category = row.category || ''
  itemForm.labor_hours = row.labor_hours
  itemForm.labor_price = row.labor_price
  itemForm.remark = ''
}

async function handleAddItem() {
  if (!selectedTemplate.value) return ElMessage.warning('请选择维修项目')
  // 新项目技师默认同第一个项目
  const items = order.value.repair_items || []
  const res = await request.post(`/work-orders/${route.params.id}/items`, {
    ...itemForm,
    template_id: selectedTemplate.value.id
  })
  const autoParts = res.data?.auto_parts || []
  let msg = '维修项目已添加'
  if (autoParts.length > 0) {
    msg += `，自动添加 ${autoParts.length} 个关联配件`
  }
  ElMessage.success(msg)
  showAddItem.value = false
  selectedTemplate.value = null
  Object.assign(itemForm, { item_name: '', item_code: '', category: '', labor_hours: 0, labor_price: 0, remark: '', charge_type: '自费', repair_category: '保养', technician_id: undefined, technician_name: undefined })
  loadOrder()
}

async function handleDeleteItem(row) {
  try {
    await request.delete(`/work-orders/${route.params.id}/items/${row.id}`)
    ElMessage.success('维修项目已删除')
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  }
}

// ==================== 备件管理 ====================
const orderParts = ref([])
const partsTotal = ref(0)
const showAddPart = ref(false)
const partsTableRef = ref(null)
const partSubmitting = ref(false)
const partsLoading = ref(false)
const partsList = ref([])
const selectedPart = ref(null)
const partKeyword = ref('')
const selectedPartStock = ref(999)
const selectedPartDefaultPrice = ref(0)
const partForm = reactive({
  part_id: null,
  quantity: 1,
  unit_price: 0,
  repair_item_id: null,
  remark: ''
})

function openAddPart() {
  partForm.part_id = null
  partForm.quantity = 1
  partForm.unit_price = 0
  partForm.repair_item_id = null
  partForm.remark = ''
  partsList.value = []
  selectedPart.value = null
  partKeyword.value = ''
  showAddPart.value = true
}

async function loadPartsList() {
  partsLoading.value = true
  try {
    const res = await request.get('/parts/list', { params: { page: 1, per_page: 50 } })
    partsList.value = res.data.items || []
  } catch (e) {
    console.error('加载配件列表失败', e)
  } finally { partsLoading.value = false }
}

async function searchParts(query) {
  if (!query) { loadPartsList(); return }
  partsLoading.value = true
  try {
    const res = await request.get('/parts/list', { params: { page: 1, per_page: 50, keyword: query } })
    partsList.value = res.data.items || []
  } catch (e) {
    console.error('搜索配件失败', e)
  } finally { partsLoading.value = false }
}

// 防抖搜索
let searchTimer = null
function onPartSearchInput(query) {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => searchParts(query), 300)
}

const filteredParts = computed(() => {
  if (!partKeyword.value) return partsList.value
  const kw = partKeyword.value.toLowerCase()
  return partsList.value.filter(p =>
    (p.part_no && p.part_no.toLowerCase().includes(kw)) ||
    (p.name && p.name.toLowerCase().includes(kw))
  )
})

function onPartCurrentChange(row) {
  if (!row) return
  if (!row.stock_quantity || row.stock_quantity <= 0) {
    ElMessage.warning('该配件库存为0，无法添加')
    return
  }
  selectedPart.value = row
  partForm.part_id = row.id
  partForm.unit_price = Number(row.selling_price || 0)
  selectedPartDefaultPrice.value = Number(row.selling_price || 0)
  selectedPartStock.value = row.stock_quantity
  partForm.quantity = 1
}

async function handleAddPart() {
  if (!partForm.part_id) return ElMessage.warning('请选择配件')
  if (!partForm.quantity || partForm.quantity < 1) return ElMessage.warning('数量不能小于1')
  if (partForm.unit_price < selectedPartDefaultPrice.value) return ElMessage.warning(`单价不能低于默认价 ¥${selectedPartDefaultPrice.value.toFixed(2)}`)

  partSubmitting.value = true
  try {
    await request.post(`/work-orders/${route.params.id}/parts`, {
      part_id: partForm.part_id,
      quantity: partForm.quantity,
      unit_price: partForm.unit_price,
      repair_item_id: partForm.repair_item_id || null,
      remark: partForm.remark
    })
    ElMessage.success('备件添加成功')
    showAddPart.value = false
    loadOrder()
  } catch (e) {
    // 错误信息已在拦截器中处理
  } finally { partSubmitting.value = false }
}

async function handlePartQtyChange(row, newQty) {
  if (newQty === null || newQty === undefined) return
  if (newQty < 0) { loadOrder(); return }

  try {
    const res = await request.put(`/work-orders/${route.params.id}/parts/${row.id}`, {
      quantity: newQty
    })
    ElMessage.success(res.message || '备件数量已更新')
    loadOrder()
  } catch (e) {
    // 回滚显示
    loadOrder()
  }
}

async function savePartField(row, field, value) {
  try {
    await request.put(`/work-orders/${order.value.id}/parts/${row.id}`, { [field]: value })
    loadOrder()
  } catch (e) { console.error('保存失败', e) }
}

async function savePartDiscount(row, value) {
  try {
    await request.put(`/work-orders/${order.value.id}/parts/${row.id}`, { discount_rate: value })
    loadOrder()
  } catch (e) { console.error('保存折扣失败', e) }
}

async function handleRemovePart(row) {
  try {
    await request.delete(`/work-orders/${route.params.id}/parts/${row.id}`)
    ElMessage.success('备件已删除')
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  }
}

async function handlePartOutbound(row) {
  try {
    await request.put(`/work-orders/${route.params.id}/parts/${row.id}/outbound`)
    ElMessage.success('备件出库成功')
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  }
}

// ==================== 收款管理 ====================
const orderPayments = ref([])
const showAddPayment = ref(false)
const paymentSaving = ref(false)
const paymentForm = reactive({
  amount: 0,
  payment_method: '',
  payer_name: '',
  remark: ''
})


function openAddPayment() {
  if (unpaidAmount.value <= 0) return ElMessage.warning('已经完成收款，请勿重复收款!')
  paymentForm.amount = Number(unpaidAmount.value.toFixed(2))
  paymentForm.payment_method = ''
  paymentForm.payer_name = order.value?.customer_name || ''
  paymentForm.remark = ''
  showAddPayment.value = true
}

async function handleAddPayment() {
  if (!paymentForm.amount || paymentForm.amount <= 0) return ElMessage.warning('请输入收款金额')
  if (!paymentForm.payment_method) return ElMessage.warning('请选择收款方式')
  if (!paymentForm.payer_name || !paymentForm.payer_name.trim()) return ElMessage.warning('请输入付款人')
  paymentSaving.value = true
  try {
    await request.post('/finance/payments', {
      order_id: order.value.id,
      customer_id: order.value.customer_id,
      amount: paymentForm.amount,
      payment_method: paymentForm.payment_method,
      payer_name: paymentForm.payer_name,
      remark: paymentForm.remark
    })
    ElMessage.success('收款成功')
    showAddPayment.value = false
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    paymentSaving.value = false
  }
}

// ==================== 开票管理 ====================
const orderInvoices = ref([])
const showAddInvoice = ref(false)
const invoiceSaving = ref(false)
const invoiceForm = reactive({
  title: '',
  tax_no: '',
  amount: 0,
  tax_amount: 0,
  invoice_type: 'normal'
})

function openAddInvoice() {
  invoiceForm.title = ''
  invoiceForm.tax_no = ''
  invoiceForm.amount = Number(unpaidAmount.value.toFixed(2))
  invoiceForm.tax_amount = 0
  invoiceForm.invoice_type = 'normal'
  showAddInvoice.value = true
}

function resetInvoiceForm() {
  Object.assign(invoiceForm, { title: '', tax_no: '', amount: 0, tax_amount: 0, invoice_type: 'normal' })
}

async function handleAddInvoice() {
  if (!invoiceForm.title || !invoiceForm.title.trim()) return ElMessage.warning('请输入发票抬头')
  if (!invoiceForm.amount || invoiceForm.amount <= 0) return ElMessage.warning('请输入开票金额')
  invoiceSaving.value = true
  try {
    await request.post('/finance/invoices', {
      ...invoiceForm,
      order_id: order.value.id,
      customer_id: order.value.customer_id
    })
    ElMessage.success('发票创建成功')
    showAddInvoice.value = false
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    invoiceSaving.value = false
  }
}

async function handleIssueInvoice(row) {
  try {
    await request.put(`/finance/invoices/${row.id}/issue`)
    ElMessage.success('发票已开具')
    loadOrder()
  } catch (e) {
    // 错误已在拦截器中处理
  }
}

// ==================== 通用方法 ====================
function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }
function formatOperation(op) {
  if (!op) return ''
  if (op === 'create') return '创建工单'
  const m = op.match(/status_change_(\d+)_to_(\d+)/)
  if (m) {
    const names = ['在修', '结算']
    return `${names[m[1]] || m[1]} → ${names[m[2]] || m[2]}`
  }
  return op
}
function getStatusType(s) { return s === 1 ? 'success' : 'primary' }

async function loadOrder() {
  loading.value = true
  try {
    const res = await request.get(`/work-orders/${route.params.id}`)
    order.value = res.data
    // 从详情中获取备件信息
    orderParts.value = res.data.order_parts || []
    partsTotal.value = orderParts.value.reduce((sum, p) => sum + Number(p.total_price || 0), 0)
    // 获取收款记录
    orderPayments.value = res.data.payments || []
    // 获取开票记录
    orderInvoices.value = res.data.invoices || []
    // 加载技师列表（用于维修项目派工）
    loadTechnicianList()
    // 重置手动修改记录
    manualEditedItems.clear()
  } finally { loading.value = false }
}

// 监听编辑按钮打开时填充表单
import { watch } from 'vue'
watch(showEditBase, (val) => { if (val) openEditBase() })
watch(showEditCost, (val) => { if (val) openEditCost() })

onMounted(() => { loadOrder(); loadDictList() })
</script>

<style scoped>
/* ==================== 状态卡片 ==================== */
.status-card {
  margin-bottom: 20px;
  border: none;
  background: linear-gradient(135deg, #f0f5ff 0%, #fafbff 100%);
}

.status-card :deep(.el-card__body) {
  padding: 24px 32px;
}

.status-card-body {
  display: flex;
  align-items: center;
  gap: 60px;
}

/* ==================== 步骤条 ==================== */
.status-steps {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 4px 0;
}

.status-step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-node {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  background: #e8ecf1;
  color: #a0aec0;
  border: 2.5px solid #e8ecf1;
  box-sizing: border-box;
}

/* 已完成 */
.status-step-item.completed .step-node {
  background: #34c759;
  color: #fff;
  border-color: #34c759;
  box-shadow: 0 2px 10px rgba(52, 199, 89, 0.3);
}

/* 当前激活 */
.status-step-item.active .step-node {
  background: #fff;
  color: #0071e3;
  border-color: #0071e3;
  box-shadow: 0 0 0 5px rgba(0, 113, 227, 0.1);
  animation: pulse-ring 2s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% { box-shadow: 0 0 0 5px rgba(0, 113, 227, 0.1); }
  50% { box-shadow: 0 0 0 10px rgba(0, 113, 227, 0.05); }
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #0071e3;
}

.step-num {
  font-size: 13px;
  color: #a0aec0;
}

/* 标签文字 */
.step-label {
  margin-top: 10px;
  font-size: 13px;
  color: #a0aec0;
  white-space: nowrap;
  transition: all 0.3s ease;
  font-weight: 400;
}

.status-step-item.completed .step-label {
  color: #34c759;
  font-weight: 500;
}

.status-step-item.active .step-label {
  color: #0071e3;
  font-weight: 600;
}

/* 连接线 */
.step-line {
  flex: 1;
  min-width: 20px;
  max-width: 30px;
  height: 1px;
  background: #e2e8f0;
  border-radius: 2px;
  margin: 17px -2px 0 -2px;
  transition: background 0.4s ease;
}

.step-line.active {
  background: #34c759;
}

/* ==================== 并行分支 ==================== */
.parallel-branch {
  display: flex;
  align-items: center;
  gap: 0;
}
.parallel-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.parallel-item .step-node {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #dcdfe6;
  background: #f5f7fa;
  color: #a0aec0;
  font-size: 14px;
  transition: all 0.3s ease;
}
.parallel-item.completed .step-node {
  background: #34c759;
  color: #fff;
  border-color: #34c759;
  box-shadow: 0 2px 10px rgba(52, 199, 89, 0.3);
}
.parallel-item.active .step-node {
  background: #fff;
  color: #0071e3;
  border-color: #0071e3;
  box-shadow: 0 0 0 5px rgba(0, 113, 227, 0.1);
  animation: pulse-ring 2s ease-in-out infinite;
}
.parallel-item .step-label {
  margin-top: 10px;
  font-size: 13px;
  color: #a0aec0;
  white-space: nowrap;
  transition: all 0.3s ease;
  font-weight: 400;
}
.parallel-item.completed .step-label {
  color: #34c759;
  font-weight: 500;
}
.parallel-item.active .step-label {
  color: #0071e3;
  font-weight: 600;
}
.parallel-divider {
  color: #c0c4cc;
  font-size: 18px;
  font-weight: bold;
  margin: 0 2px;
  padding-bottom: 22px;
}

/* ==================== 操作按钮 ==================== */
.status-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}
</style>
