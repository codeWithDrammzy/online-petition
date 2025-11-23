{% extends "peptitions/main.html" %}

{% block content %}
<!-- Welcome Header -->
<div class="mb-8">
  <h1 class="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
  <p class="text-gray-600 mt-2">Welcome back, {{ user }}! Here's what's happening with your petitions today.</p>
</div>

<!-- Quick Stats Grid -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
  <!-- Total Petitions -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-300">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">Total Petitions</p>
        <p class="text-3xl font-bold text-gray-900 mt-1">{{ total_petitions }}</p>
      </div>
      <div class="p-3 bg-blue-100 rounded-xl">
        <i class="fas fa-scroll text-blue-600 text-2xl"></i>
      </div>
    </div>
    <div class="mt-4 flex items-center text-sm text-green-600">
      <i class="fas fa-arrow-up mr-1"></i>
      <span>All active campaigns</span>
    </div>
  </div>

  <!-- Pending Petitions -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-300">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">Pending Review</p>
        <p class="text-3xl font-bold text-gray-900 mt-1">{{ pending_petitions }}</p>
      </div>
      <div class="p-3 bg-yellow-100 rounded-xl">
        <i class="fas fa-clock text-yellow-600 text-2xl"></i>
      </div>
    </div>
    <div class="mt-4 flex items-center text-sm text-yellow-600">
      <i class="fas fa-exclamation-circle mr-1"></i>
      <span>Needs attention</span>
    </div>
  </div>

  <!-- Total Users -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-300">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">Total Users</p>
        <p class="text-3xl font-bold text-gray-900 mt-1">{{ total_users }}</p>
      </div>
      <div class="p-3 bg-green-100 rounded-xl">
        <i class="fas fa-users text-green-600 text-2xl"></i>
      </div>
    </div>
    <div class="mt-4 flex items-center text-sm text-blue-600">
      <i class="fas fa-user-plus mr-1"></i>
      <span>Community members</span>
    </div>
  </div>
</div>

<!-- Main Content Grid -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
  <!-- Recent Petitions -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold text-gray-900">Recent Petitions</h2>
      <a href="{% url 'petition-list' %}" class="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center">
        View all
        <i class="fas fa-arrow-right ml-2 text-xs"></i>
      </a>
    </div>
    
    <div class="space-y-4">
      {% for petition in recent_petitions %}
      <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-colors duration-200 border border-gray-200">
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-gray-900 truncate">{{ petition.title }}</h3>
          <p class="text-sm text-gray-600 mt-1 truncate">{{ petition.description|truncatewords:10 }}</p>
        </div>
        <div class="flex items-center space-x-4 ml-4">
          <span class="text-xs px-3 py-1 rounded-full font-medium
            {% if petition.status == 'pending' %}
              bg-yellow-100 text-yellow-800 border border-yellow-200
            {% elif petition.status == 'approved' %}
              bg-green-100 text-green-800 border border-green-200
            {% else %}
              bg-red-100 text-red-800 border border-red-200
            {% endif %}">
            {{ petition.status|title }}
          </span>
          <a href="{% url 'petition-list' %}" class="text-blue-600 hover:text-blue-700">
            <i class="fas fa-chevron-right"></i>
          </a>
        </div>
      </div>
      {% empty %}
      <div class="text-center py-8">
        <i class="fas fa-inbox text-gray-300 text-4xl mb-3"></i>
        <p class="text-gray-500">No recent petitions</p>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Analytics Chart -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold text-gray-900">Petitions Analytics</h2>
      <div class="flex items-center space-x-2 text-sm text-gray-500">
        <i class="fas fa-chart-pie"></i>
        <span>Status Distribution</span>
      </div>
    </div>
    <div class="h-64">
      <canvas id="petitionChart"></canvas>
    </div>
    <div class="mt-4 grid grid-cols-3 gap-4 text-center">
      {% for status, count in status_counts %}
      <div class="text-center">
        <div class="text-lg font-bold text-gray-900">{{ count }}</div>
        <div class="text-sm text-gray-600 capitalize">{{ status }}</div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>

<!-- Quick Actions -->
<div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
  <h2 class="text-xl font-bold text-gray-900 mb-6">Quick Actions</h2>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <a href="{% url 'petition-list' %}" class="flex items-center p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors duration-200 border border-blue-200 group">
      <div class="p-3 bg-blue-100 rounded-lg mr-4 group-hover:scale-110 transition-transform duration-200">
        <i class="fas fa-list text-blue-600 text-xl"></i>
      </div>
      <div>
        <p class="font-semibold text-blue-700">Manage Petitions</p>
        <p class="text-sm text-blue-600 mt-1">View and manage all</p>
      </div>
    </a>

    <a href="{% url 'user-list' %}" class="flex items-center p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors duration-200 border border-green-200 group">
      <div class="p-3 bg-green-100 rounded-lg mr-4 group-hover:scale-110 transition-transform duration-200">
        <i class="fas fa-users text-green-600 text-xl"></i>
      </div>
      <div>
        <p class="font-semibold text-green-700">Manage Users</p>
        <p class="text-sm text-green-600 mt-1">User management</p>
      </div>
    </a>

    <a href="#" class="flex items-center p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors duration-200 border border-purple-200 group">
      <div class="p-3 bg-purple-100 rounded-lg mr-4 group-hover:scale-110 transition-transform duration-200">
        <i class="fas fa-chart-bar text-purple-600 text-xl"></i>
      </div>
      <div>
        <p class="font-semibold text-purple-700">View Reports</p>
        <p class="text-sm text-purple-600 mt-1">Analytics & insights</p>
      </div>
    </a>

    <a href="#" class="flex items-center p-4 bg-orange-50 rounded-xl hover:bg-orange-100 transition-colors duration-200 border border-orange-200 group">
      <div class="p-3 bg-orange-100 rounded-lg mr-4 group-hover:scale-110 transition-transform duration-200">
        <i class="fas fa-cog text-orange-600 text-xl"></i>
      </div>
      <div>
        <p class="font-semibold text-orange-700">Settings</p>
        <p class="text-sm text-orange-600 mt-1">Platform config</p>
      </div>
    </a>
  </div>
</div>

<!-- Add Font Awesome for icons -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.com/npm/chart.js"></script>
<script>
  const ctx = document.getElementById('petitionChart').getContext('2d');
  const petitionChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: {{ statuses|safe }},
      datasets: [{
        data: {{ counts|safe }},
        backgroundColor: [
          'rgba(255, 193, 7, 0.8)',    // Yellow for pending
          'rgba(40, 167, 69, 0.8)',    // Green for approved
          'rgba(220, 53, 69, 0.8)',    // Red for rejected
        ],
        borderColor: [
          'rgba(255, 193, 7, 1)',
          'rgba(40, 167, 69, 1)',
          'rgba(220, 53, 69, 1)',
        ],
        borderWidth: 2,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true,
          }
        }
      },
      cutout: '60%'
    }
  });
</script>
{% endblock %}