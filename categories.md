---
layout: page
title: ジャンル別一覧
permalink: /categories/
---

{% for category in site.categories %}
  <h2 id="{{ category[0] | slugify }}">{{ category[0] }}（{{ category[1].size }}件）</h2>
  <ul>
    {% for post in category[1] %}
      <li>
        <span style="color: #666; font-size: 0.9em;">{{ post.date | date: "%Y/%m/%d" }}</span> -
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      </li>
    {% endfor %}
  </ul>
{% endfor %}
