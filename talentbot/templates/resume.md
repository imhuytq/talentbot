# {{ name }}
{% if label %}
{{ label }}
{% endif %}

{% if gender -%}
| **Gender**: {{ gender }} |
{% endif -%}
{% if dob -%}
| **Date of Birth**: {{ dob }} |
{% endif -%}
{% if email -%}
| **Email**: {{ email }} |
{% endif -%}
{% if phone -%}
| **Phone**: {{ phone }} |
{% endif -%}
{% if url -%}
| **Website**: {{ url }} |
{% endif -%}

{% if profiles %}
{% for profile in profiles -%}
| **{{ profile.network }}**: [{{ profile.username }}]({{ profile.url }}) |
{% endfor -%}
{% endif -%}

{% if location %}
**Location**: {{ location.address }}, {{ location.city }}, {{ location.region }}, {{ location.postal_code }}, {{ location.country_code }}
{% endif -%}

{% if objective -%}
## Objective
{{ objective }}
{% endif -%}

{% if education %}
## Education

| Institution    | Area | Degree | Period | Score | Courses |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
{% for edu in education -%}
| {{ edu.institution }} | {{ edu.area }} | {{ edu.study_type }} | {% if edu.start_date %}{{ edu.start_date }}{% if edu.end_date %} to {{ edu.end_date }}{% endif %}{% endif %} | {{ edu.score }} | {% if edu.courses %}{% for course in edu.courses %}- {{ course }}<br />{% endfor %}{% endif %} |
{% endfor %}
{% endif %}

{% if work %}
## Work Experience

| Job    | Period | Position | Summary | Highlights |
| ----------- | ----------- | ----------- | ----------- | ----------- |
{% for job in work -%}
| {% if job.url %}[{{ job.name }}]({{ job.url }}){% else %}{{ job.name }}{% endif %} | {% if job.start_date %}{{ job.start_date }}{% if job.end_date %} to {{ job.end_date }}{% endif %}{% endif %} | {{ job.position }} | {{ job.summary | replace("\n", "<br>") }} | {% if job.highlights %}{% for highlight in job.highlights %}- {{ highlight }}<br />{% endfor %}{% endif %} |
{% endfor %}
{% endif %}

{% if volunteer %}
## Volunteer Experience

| Organization    | Period | Position | Summary | Highlights |
| ----------- | ----------- | ----------- | ----------- | ----------- |
{% for vol in volunteer -%}
| {% if vol.url %}[{{ vol.name }}]({{ vol.url }}){% else %}{{ vol.name }}{% endif %} | {% if vol.start_date %}{{ vol.start_date }}{% if vol.end_date %} to {{ vol.end_date }}{% endif %}{% endif %} | {{ vol.position }} | {{ vol.summary }} | {% if vol.highlights %}{% for highlight in vol.highlights %}- {{ highlight }}<br />{% endfor %}{% endif %} |
{% endfor %}
{% endif %}


{% if awards %}
## Awards

| Title    | Date | Awarder | Summary |
| ----------- | ----------- | ----------- | ----------- |
{% for a in awards -%}
| {{ a.title }} | {{ a.date }} | | {{ a.awarder }} | | {{ a.summary }} |
{% endfor %}
{% endif %}


{% if certificates %}
## Certificates

| Name    | Date | Issuer | Url |
| ----------- | ----------- | ----------- | ----------- |
{% for cert in certificates -%}
| {{ cert.name }} | {{ cert.date }} | | {{ cert.issuer }} | | {{ cert.url }} |
{% endfor %}
{% endif %}

{% if publications %}
## Publications

| Name    | Publisher | Release date | Summary |
| ----------- | ----------- | ----------- | ----------- |
{% for pub in publications -%}
| {% if pub.url %}[{{ pub.name }}]({{ pub.url }}){% else %}{{ pub.name }}{% endif %} | {{ pub.publisher }} | {{ pub.release_date }} | {{ pub.summary }} |
{% endfor %}
{% endif %}

{% if skills %}
## Skills

| Skill    | Level | Keywords |
| ----------- | ----------- | ----------- |
{% for skill in skills -%}
| {{ skill.name }} | {{ skill.level }} | {% if skill.keywords %}{{ skill.keywords | join(', ') }}{% endif %} |
{% endfor %}
{% endif %}

{% if languages %}
## Languages

| Language    | Fluency |
| ----------- | ----------- |
{% for language in languages -%}
| {{ language.language }} | {{ language.fluency }} |
{% endfor %}
{% endif %}

{% if interests %}
## Interests

| Interest    | Keywords |
| ----------- | ----------- |
{% for interest in interests -%}
| {{ interest.name }} | {% if interest.keywords %}{{ interest.keywords | join(', ') }}{% endif %} |
{% endfor %}
{% endif %}

{% if references %}
## References

| Name    | Reference |
| ----------- | ----------- |
{% for reference in references -%}
| {{ reference.name }} | {{ reference.reference }} |
{% endfor %}
{% endif %}

{% if projects %}
## Projects

| Project    | Period | Description | Highlights |
| ----------- | ----------- | ----------- | ----------- |
{% for project in projects -%}
| {% if project.url %}[{{ project.name }}]({{ project.url }}){% else %}{{ project.name }}{% endif %} | {% if project.start_date %}{{ project.start_date }}{% if project.end_date %} to {{ project.end_date }}{% endif %}{% endif %} | {{ project.description }} | {% if project.highlights %}{% for highlight in project.highlights %}- {{ highlight }}<br />{% endfor %}{% endif %} |
{% endfor %}
{% endif %}

{% if prediction %}
## Predictions
### Suitable Industries
{% for industry in prediction.industries %}
- **{{ industry.name }}**: {{ industry.confidence }} confidence
{% endfor %}
{% endif %}
