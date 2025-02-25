from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.output_parsers import PydanticOutputParser

def query_classification_agent_chapters(user_query: str) -> list:
    # Define the Pydantic model
    class Query(BaseModel):
        updated_queries: list[int] = Field(
            description=(
                f"""
**Task:**  
You are an expert AI classifier specializing in Arabic business and legal terminology. Your task is to classify the user query {user_query} into one or more predefined numerical classes based on its relevance to specific corporate, commercial, and legal topics.
Classification Criteria:

Classification Criteria 
#### Class 1: General Company Regulations 
- **Example:** "ما هي المستندات المطلوبة لتأسيس شركة؟" → [1]  , كيف تاسس شركه 
if the quary related to any one these for any type of compaines 
    -Company Definition & Formation
    -Company Definition
    -Company Nationality
    -Company Types
    -Company Name
    -Company Formation Request
    -Company Formation Documents
    -Registration of Formation Documents
    -Legal Entity Acquisition
    -Company Objectives
    -Partners' Agreement & Family Charter
    -Required Company Document Information
    -Partner or Shareholder Share
    -Contribution of Shares
    -Delay in Contribution of Shares
    -Company Finance
    -Company Fiscal Year
    -Accounting Records & Financial Statements
    -Appointment, Dismissal & Resignation of Auditor
    -Non-applicability of Auditor Requirement
    -Auditor Obligations
    -Company Accounts Oversight
    -Profit Distribution
    -Profit & Loss Sharing
    -Partner's Share in Profit & Loss
    -Transfer of Shares & Stock Trading
    -Company Management
    -Duties of Care & Loyalty for example : ما هي العقوبات التي يمكن أن تفرض على المدير في حال خالف أحكام الولاء و الطاعه
    -Conflict of Interest, Competition & Asset Exploitation
    -Management Responsibility
    -Company, Partner or Shareholder Lawsuit
    -Inadmissibility of Lawsuit
    -Decision Evaluation Rule for example من يتحمل عبء إثبات أن المدير لم يتخذ قراره بحسن نية؟
    -Costs of Liability Lawsuit
    -Execution on Partner or Shareholder Profits
    -Execution on Shares & Stocks
        -This class covers legal provisions from Article 1 to Article 34. Any article number within this range (المادة 1، المادة 2، المادة 3، المادة 4، المادة 5، المادة 6، المادة 7، المادة 8، المادة 9، المادة 10، المادة 11، المادة 12، المادة 13، المادة 14، المادة 15، المادة 16، المادة 17، المادة 18، المادة 19، المادة 20، المادة 21، المادة 22، المادة 23، المادة 24، المادة 25، المادة 26، المادة 27، المادة 28، المادة 29، المادة 30، المادة 31، المادة 32، المادة 33، والمادة 34) belongs to Class 1. Ensure that all articles within this range are included  
        any question outside those Article dont belonge to this class
#### Class 2: General Partnership Companies (شركة التضامن)**  

    - **Example:** "ما هي حقوق والتزامات الشركاء في شركة التضامن؟" → [2]  
    - Covers the legal framework for **partnership companies**, including their **formation, management, partner rights, financial obligations, and dissolution**.  
    - the query should be  related to Partnership Companies
    -this class covers the legal provisions starting from المادة الخامسة والثلاثون (Article 35) and ending at المادة الخمسون (Article 50). Any article number within this range (المادة 35، المادة 36، المادة 37، المادة 38، المادة 39، المادة 40، المادة 41، المادة 42، المادة 43، المادة 44، المادة 45، المادة 46، المادة 47، المادة 48، المادة 49، والمادة 50) belongs to Class 2

#### Class 3: Limited Partnership Companies (شركة التوصية البسيطة)**  
    - **Example:** "ما دور الشريك الموصي في شركة التوصية البسيطة؟" → [3]  
    - Addresses the **formation, partner roles, decision-making process, and dissolution** of limited partnership companies.  
    -the query should be  related Limited Partnership Companies
    -This class covers legal provisions from Article 51 to Article 57. Any article number within this range (المادة 51، المادة 52، المادة 53، المادة 54، المادة 55، المادة 56، والمادة 57) belongs to Class 3

#### Class 4: شركات المساهمة (Joint-Stock Companies) and covers the following key areas:
        any question related to شركه المساهمه
        Examples:
        ما هي القواعد المتعلقة بتحويل الأسهم بين المساهمين؟
        ما هي عملية الاكتتاب في الأسهم خلال مرحلة التأسيس؟
        ما هي الإجراءات المتبعة في حالة تخفيض رأس مال شركة المساهمة؟
        ما هي القواعد المتعلقة بتقييم الحصص العينية في شركة المساهمة؟
        كيف يمكن للمساهمين مراقبة أعمال مجلس الإدارة في شركة المساهمة؟
        ما هي القيود المفروضة على تداول الأسهم في شركة المساهمة؟
        ما الفرق بين رأس المال المصدر ورأس المال المصرح به؟
        ما هي الشروط التي يمكن لمجلس الإدارة زيادة رأس المال المصدر بموجبها؟
        ما هي القواعد المتعلقة بتقييم الحصص العينية؟
        ما هي الحقوق والالتزامات المرتبطة بالأسهم؟
        ما هي الإجراءات المتبعة في حالة خسارة نصف رأس مال الشركة؟
        ما هي حقوق المساهمين في حضور الاجتماعات والتصويت على القرارات؟
    -This class covers legal provisions from Article 58 to Article 137. Any article number within this range (المادة 59، المادة 60، المادة 61، المادة 62، المادة 63، المادة 64، المادة 65، المادة 66، المادة 67، المادة 68، المادة 69، المادة 70، المادة 71، المادة 72، المادة 73، المادة 74، المادة 75، المادة 76، المادة 77، المادة 78، المادة 79، المادة 80، المادة 81، المادة 82، المادة 83، المادة 84، المادة 85، المادة 86، المادة 87، المادة 88، المادة 89، المادة 90، المادة 91، المادة 92، المادة 93، المادة 94، المادة 95، المادة 96، المادة 97، المادة 98، المادة 99، المادة 100، المادة 101، المادة 102، المادة 103، المادة 104، المادة 105، المادة 106، المادة 107، المادة 108، المادة 109، المادة 110، المادة 111، المادة 112، المادة 113، المادة 114، المادة 115، المادة 116، المادة 117، المادة 118، المادة 119، المادة 120، المادة 121، المادة 122، المادة 123، المادة 124، المادة 125، المادة 126، المادة 127، المادة 128، المادة 129، المادة 130، المادة 131، المادة 132، المادة 133، المادة 134، المادة 135، المادة 136، والمادة 137) belongs to Class 4. Ensure that all articles within this range are included and addressed in the analysis or discussion.


#### Class 5: Simplified Joint Stock Company (شركة المساهمة المبسطة) 
    - Focuses on the legal framework of simplified joint stock companies, including their formation and governance.  
    - note : the query should be  related Simplified Joint Stock Company  
    -This class covers legal provisions from Article 138 to Article 155. Any article number within this range (المادة 138، المادة 139، المادة 140، المادة 141، المادة 142، المادة 143، المادة 144، المادة 145، المادة 146، المادة 147، المادة 148، المادة 149، المادة 150، المادة 151، المادة 152، المادة 153، المادة 154، والمادة 155) belongs to Class 5
    -**Example:** "كيف يتم تأسيس شركة مساهمة مبسطة؟" → [5]  

#### Class 6: Limited Liability Company (الشركة ذات المسؤولية المحدودة) 
    -note :the query should be  related Limited Liability Companies (الشركة ذات المسؤولية المحدودة) 
    -This class covers legal provisions from Article 156 to Article 184. Any article number within this range (المادة 156، المادة 157، المادة 158، المادة 159، المادة 160، المادة 161، المادة 162، المادة 163، المادة 164، المادة 165، المادة 166، المادة 167، المادة 168، المادة 169، المادة 170، المادة 171، المادة 172، المادة 173، المادة 174، المادة 175، المادة 176، المادة 177، المادة 178، المادة 179، المادة 180، المادة 181، المادة 182، المادة 183، والمادة 184) belongs to Class 6

#### Class 7: Non-Profit Companies (الشركات غير الربحية)  جمعية خيرية - الجمعيات الخيرية - غير ربحي**  
    - Example:"ما هي اللوائح القانونية للشركات غير الربحية؟" → [7]  
    - Covers legal aspects of **non-profit organizations**, which serve societal or charitable purposes **without profit distribution** to members or shareholders.  
    - the query should be related non-profit companies 
    -This class covers legal provisions from Article 185 to Article 196. Any article number within this range (المادة 186، المادة 187، المادة 188، المادة 189، المادة 190، المادة 191، المادة 192، المادة 193، المادة 194، والمادة 195) belongs to Class 

####Class 8: any quary  related to Professional Companies (الشركات المهنية)**  
  -cover Professional Companies
  -This class covers legal provisions from Article 197 to Article 215. Any article number within this range (المادة 198، المادة 199، المادة 200، المادة 201، المادة 202، المادة 203، المادة 204، المادة 205، المادة 206، المادة 207، المادة 208، المادة 209، المادة 210، المادة 211، المادة 212، المادة 213، والمادة 214) belongs to Class 8.
  Example Belonging to Class 8:

        "ما هي الشركة المهنية؟"
        كيف يتم التعامل مع وفاة شريك أو مساهم في الشركة المهنية، وما تأثير ذلك على استمرار الشركة؟
        هل يُشترط على الشركات المهنية الحصول على تغطية تأمينية للأخطاء المهنية؟ ولماذا؟
        هل يمكن للشخص الواحد أن يكون شريكًا أو مساهمًا في أكثر من شركة مهنية في نفس المجال؟ ولماذا؟
        كيف يمكن حل الشركة المهنية وما الإجراءات المطلوبة لذلك؟
        هل يجوز للشركة المهنية ممارسة أعمال تجارية؟ وما الأنشطة المسموح بها لها؟
        ما الجهة المسؤولة عن الإشراف على الشركات المهنية، وما دورها في تنظيم أعمالها؟
        ما الشروط المطلوبة لتأسيس شركة مهنية؟
        هل يجوز لمرخص لهم في أكثر من مهنة حرة تأسيس شركة مهنية واحدة؟ وما الضوابط المحددة لذلك؟
        هل يمكن لشخص غير مرخص له بممارسة المهنة أن يساهم في شركة مهنية؟ وما الشروط المنظمة لذلك؟
        ما تعريف الشركة المهنية وما الهدف من تأسيسها؟
        ما الأشكال القانونية التي يمكن أن تتخذها الشركة المهنية؟
        هل يكتسب الشريك أو المساهم في الشركة المهنية صفة التاجر؟ ولماذا؟
        
#### **Class 9: any quary  related to Holding Companies (الشركة القابضة) & Subsidiaries(والشركة التابعة)**  
    -This class covers legal provisions from Article 216 to Article 219. Any article number within this range (المادة 217، المادة 218، والمادة 219) belongs to Class 9


#### **Class 10: Companies  Transformation (تحول الشركات واندماجها وتقسيمها  )  
- Example "ما هي إجراءات تحويل شركة تضامن إلى شركة مساهمة؟" → [10]  
- Legal process of converting a company from one type to another 
cover all topics : 
    Company Transformation & Mergers from any type for example ما هي الشروط الرئيسية لتحول الشركة إلى شركة مساهمة مبسطة؟
Company Transformation
    Company Transformation to Another Form 
    Transformation of Non-Profit Company
    Objection to Transformation Decision
    Company Identity After Transformation
    Release of Liability for General Partners
Company Mergers
    Merger Proposal
    Merger into a Parent Company
    Objection to Merger Decision
    Effectiveness of Merger Decision
    Rights, Obligations, Assets & Contracts of Merged Company
    Obligation to Buy & Sell Shares
-Company Division
    Form of Company Created by Division
    Division Decision
    Debts & Obligations of Divided Company
    Division Regulations
-This class covers legal provisions from Article 220 to Article 234. Any article number within this range (المادة 221، المادة 222، المادة 223، المادة 224، المادة 225، المادة 226، المادة 227، المادة 228، المادة 229، المادة 230، المادة 231، المادة 232، المادة 233، والمادة 234) belongs to Class 10.

    
###Class 11: any quary  related to Foreign Companies (الشركات الأجنبية)
    -Example: "ما هي شروط عمل الشركات الأجنبية ؟" → [11]   , ما الشروط التي يجب أن تستوفيها الشركة الأجنبية للاستمرار في المملكة بعد انتهاء القيد المؤقت؟
    
    - Regulations for foreign companies** operating within the country, including compliance and legal responsibilities. 
    cover these topics 
    Regulations for Foreign Companies Operating Within the Kingdom
    1. Scope of Application
        Defines the types of foreign companies subject to the legal framework.
        Specifies conditions for their operation within the Kingdom.
    2. Business Operations and Compliance
        Regulations governing foreign company activities.
        Requirements for registration and legal compliance.
    3. Documentation and Transparency
        Mandatory information to be included in company documents.
        Ensuring legal compliance and transparency.
    4. Financial Obligations
        Accounting practices and financial responsibilities for company branches.
        Compliance with financial reporting regulations.
    5. Legal Domicile and Jurisdiction
        Definition of a foreign company's legal domicile within the Kingdom.
        Impact on jurisdiction and legal responsibilities.
    This class covers legal provisions from Article 235 to Article 241. Any article number within this range (المادة 236، المادة 237، المادة 238، المادة 239، المادة 240، والمادة 241) belongs to Class 11. 

### Class 12: any quary  related to  Company Liquidation and Management During Liquidation Period (تصفية الشركات)   
    - Example:"ما هي إجراءات تصفية الشركات؟" → [12]  
    - Covers  
    any question related to Company Liquidation and Management During Liquidation Period
    1. Financial Examination and Dissolution Causes
        Reviewing the company's financial status and required assessments.
        Identifying legal and financial reasons for dissolution.
    2. Liquidation Procedures
        Legal and administrative steps for dissolving a company.
        Distribution of assets and settlement of obligations.
    3. Management During Liquidation
        Responsibilities in operating and closing the company.
        Decision-making during the liquidation period.
    4. Appointment and Role of Liquidators
        Number of liquidators required and duration of liquidation.
        Criteria and decision-making process for appointing liquidators.
        Registration and publication of liquidator appointments.
        Grounds and procedures for dismissing a liquidator.
        Rules for multiple liquidators handling liquidation.
    5. Liquidator's Powers and Responsibilities
        Authority in managing assets, settling debts, and making liquidation-related decisions.
        Inventory of company assets and liabilities.
    6. Handling Financial Obligations
        Managing scenarios where assets are insufficient to cover liabilities.
        Prioritization and settlement of outstanding debts.
        Special considerations for non-profit company assets.
    7. Completion of Liquidation
        Final settlement of financial matters.
        Legal closure of the company.
        8. Liquidator's Liability and Legal Considerations
        Accountability for mismanagement during liquidation.
        Time limitations for liability claims against the liquidator.
    This class covers legal provisions from Article 242 to Article 259. Any article number within this range (المادة 243، المادة 244، المادة 245، المادة 246، المادة 247، المادة 248، المادة 249، المادة 250، المادة 251، المادة 252، المادة 253، المادة 254، المادة 255، المادة 256، المادة 257، المادة 258، والمادة 259) belongs to Class 12



#### Class 13: Corporate Legal Penalties & Regulatory Oversight
    - Example: "ما هي العقوبات القانونية ضد الشركات المخالفة؟" → [13]   , ما هي الصلاحيات التي تتمتع بها الجهات الرقابية تجاه الشركات؟
ما هي التزامات مسؤولي الشركات تجاه الجهات الرقابية؟      

    - Addresses:  
    Regulations on Violations, Penalties, and Oversight
1. Criminal Offenses and Penalties
    Penalties for severe offenses.
    Penalties for less severe offenses.
    Sanctions for regulatory violations.
2. Determination and Alternatives to Penalties
    Criteria for determining penalties.
    Alternative sanctions and corrective measures.
3. Investigation and Judicial Authority
    Authorities responsible for investigation and prosecution.
    Jurisdiction of the competent judicial body.
    Role of the committee reviewing violations.
4. Law Enforcement and Compensation
    Law enforcement powers for regulatory violations.
    Procedures for seeking compensation for damages.
5. Corporate Oversight and Transparency
    Monitoring and regulatory oversight of companies.
    Access to company records and official documents.
   This class covers legal provisions from Article 260 to Article 271. Any article number within this range (المادة 261، المادة 262، المادة 263، المادة 264، المادة 265، المادة 266، المادة 267، المادة 268، المادة 269، المادة 270، والمادة 271) belongs to Class 13

### Output Format:
The output should be a Python list containing only the **numerical class IDs without names.  

Classify the query accordingly and return a list of numbers only
can classifiy the qaury into muilte classes 
instrucations: 
    -Any query related to Companies Transformation, including mergers, divisions, and conversions (تحول الشركات واندماجها وتقسيمها), must be classified as Class 10.
    -if the query desent belong to any class return [0]
    -if the user asks about a specific Article or المادة number, identify and select the class that includes this article number.
    
"""
            )
        )

    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    # Initialize the Pydantic output parser
    output_parser = PydanticOutputParser(pydantic_object=Query)

    # Define the chat prompt template
    prompt = ChatPromptTemplate.from_template("""

    Instructions:
                                              

    {format_instructions}
                                              

""")
    
    # Format the prompt with the instructions and parser format
    formatted_prompt = prompt.format_messages(
        prompt_=prompt,
        format_instructions=output_parser.get_format_instructions()
    )
    # Get the LLM response
    response = llm.invoke(formatted_prompt)

    # Parse the LLM's response
    parsed_response = output_parser.parse(response.content)

    # Print the search queries
    return parsed_response.updated_queries 

# to get most simialr questions with answer 
def query_classification_agent_qa(user_query: str) -> list:
    # Define the Pydantic model
    class Query(BaseModel):
        updated_queries: list[int] = Field(
            description=(
                f"""
You are an expert AI classifier specializing in Arabic business and legal terminology. Your task is to classify the user query {user_query} into one or more predefined numerical classes based on its relevance to specific corporate, commercial, and legal topics.
Classification Criteria:
###Class 1: الأنشطة - الدليل الوطني للأنشطة ISIC4 - رمز النشاط
    questions exmple "كيف يمكن إستخراج رمز تجاري في حال عدم وجود سجل تجاري؟",



### Class 2: الإمتياز التجاري - الفرانشايز - Franchise
    this class cover questions like this : 
        What is a franchise?
        Who are the franchisor (مانح الامتياز) and franchisee (صاحب الامتياز)?
        How does the franchise system work in Saudi Arabia?
        Difference between a franchise agreement and commercial agency agreement.
    Franchise Regulations & Compliance
        Legal framework and applicability of the Franchise Law.
        The process of registering a franchise agreement with the Ministry of Commerce.
        Requirements for disclosure documents (وثيقة الإفصاح).
        Conditions for modifying or canceling a registered franchise.
    Franchise Services & Procedures
        How to create, modify, or cancel a franchise registration.
        Required documents for franchise registration.
        Online platforms for registration and processing services.
        Fees for franchise services (e.g., 500 SAR for new registration, 100 SAR for modifications).
    Franchise Business Model & Operation
        How franchising operates in Saudi Arabia.
        Responsibilities of the franchisor and franchisee.
        The importance of brand licensing and operational guidelines.
### Class 3: الاسم التجاري - الأسماء التجارية
    this class cover questions like Main Topics Covered 
         an query related to Commercial Name Reservation & Usage
         trade name reservation , focusing on requirements, approval, rejections, validity, and processes. Key points: 

### Class 4: التراخيص - الترخيص - رخصة
    cover business licenses and their management

### Class 5:any questions related to  الجمعية العادية والجمعية الغير عادية 
    Covers regulations regarding general and extraordinary assemblies.

###Class 6: السجل التجاري - السجلات التجارية - السجل التجاري الفرعي
    Covers commercial registration and related records.

##Class 7: الشركات المختلطة - الأجانب - المقيمين
    Covers foreign participation in companies and mixed ownership regulations.
##Class 8: الشركات المساهمة - المساهمة البسيطة - المساهمة المبسطة
    for example 'أين يمكن تعديل نظام الأساس للشركات المساهمة /المساهمة المبسطة؟
    Covers joint stock companies (simplified or standard).

##Class 9: الشركات المهنية - مهني - استشاري
    Example: 'ما هي شروط ومتطلبات شطب الترخيص المهني؟',
    
###Class 10: الشركات الوقفية - شركة وقفية - وقف - أوقاف
    example كيف يتم حجز اسم تجاري للأوقاف؟'
    
###Class 11: المؤسسة - مؤسسة فردية - شركة فردية
  cover questions like in this domains
        Business Conversion: Changing a sole proprietorship to a company or branch, and vice versa.
        Registration & Licensing: Issuing commercial registrations for Waqf foundations, GCC nationals, and trade name reservations.
        Ownership Transfer: Rules on transferring business ownership, especially for government employees and deceased owners.
        Modification & Cancellation: Amending or canceling business registrations, including special cases.
        Regulations & Operations: Restrictions on combining activities, appointing managers, and foreign ownership rules.
        Fees & Costs: Costs of issuing or renewing commercial registrations.
        General Clarifications: Differences between sole proprietorships and companies, and legal requirements for business owners
        Example: "ما الفرق بين المؤسسة الفردية والشركة الفردية؟" → [11]
###Class 12: المخالفات - مخالفة لنظام الشركات - الجرائم
Example: "ما هي العقوبات المفروضة على الشركات المخالفة؟" → [12]

Class 13: الوكالة التجارية - الوكالات التجارية
    covers these topics 
        Submission & Access: How to submit, modify, renew, or cancel a commercial agency registration and where to find it online.
        Fees & Costs: Whether there are fees for services like registration, renewal, cancellation, and modifications.
        Regulations & Requirements: The conditions for registering a commercial agency, including necessary documents and legal stipulations.
        Verification & Printing: How to verify an agency's registration status and whether certificates can be printed, including for expired agencies.
###Class 14: تصفية ودمج الشركات - تصفية شركة - دمج شركة
    Example: "كيف يتم تصفية شركة ذات مسؤولية محدودة؟" → [14]
    Covers corporate liquidation, mergers, and restructuring.
###Class 15: جمعية خيرية - الجمعيات الخيرية - غير ربحي
    Covers non-profit organizations and charitable entities.
###Class 16: سجل المساهمين - المساهمين - الأسهم
    Example: ماهي آلية تعديل عدد الأسهم ؟   , ماهي آلية تحديث سجل المساهمين ؟
    Covers shareholder records, stock distribution, and related legal aspects.
###Class 17: شركة ذات مسؤولية محدودة - شركات التضامن - شركات التوصية البسيطة
    this classs covers Regulations, Procedures, and Fees for Limited Liability, Partnership, and Simple Partnership Companies
    Example:  'ما المطلوب من مدير الشركة ذات المسؤولية المحدودة في حال بلغت خسائر الشركة نصف رأس المال ؟',
###Class 18: عقد التأسيس - عقد تأسيس شركة - قرارات الشركاء any qury related to this topic 
    Example: "ما هي البنود الأساسية في عقد تأسيس شركة؟" → [18]
    Covers company incorporation contracts and partner agreements.
###Class 19: متجر الكتروني - متاجر الكترونية
    Example: "كيف أسجل متجري الإلكتروني؟" → [19]
    Covers e-commerce business regulations.

### Output Format:
The output should be a **Python list** containing only the numerical class IDs without names.  

Classify the query accordingly and return a list of numbers only
can classifiy the qaury into muilte classes 
instrucations: 
    if the query desent belong to any class return [0]
    -GIVE HIGH PERORTY FOR LAST QUERY 


"""
            )
        )

    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    # Initialize the Pydantic output parser
    output_parser = PydanticOutputParser(pydantic_object=Query)

    # Define the chat prompt template
    prompt = ChatPromptTemplate.from_template("""

    Instructions:
                                              

    {format_instructions}
                                              

""")
    # Format the prompt with the instructions and parser format
    formatted_prompt = prompt.format_messages(
        prompt_=prompt,
        format_instructions=output_parser.get_format_instructions()
    )
    # Get the LLM response
    response = llm.invoke(formatted_prompt)

    # Parse the LLM's response
    parsed_response = output_parser.parse(response.content)

    # Print the search queries
    return parsed_response.updated_queries 

re_write_llm = ChatOpenAI(temperature=0, model_name="gpt-4o", max_tokens=4000)

# Create a prompt template for query rewriting
query_rewrite_template = """You are an AI assistant tasked with reformulating user queries to improve retrieval in a RAG system. 
Given the original query, rewrite it to be more specific, detailed, and likely to retrieve relevant information.

Original query: {original_query}
instrucations:
    -make the query as readable format without adding any information the output questoins how , what  


Rewritten query:"""

query_rewrite_prompt = PromptTemplate(
    input_variables=["original_query"],
    template=query_rewrite_template
)

# Create an LLMChain for query rewriting
query_rewriter = query_rewrite_prompt | re_write_llm

def rewrite_query(original_query):
    """
    Rewrite the original query to improve retrieval.
    
    Args:
    original_query (str): The original user query
    
    Returns:
    str: The rewritten query
    """
    response = query_rewriter.invoke(original_query)
    return response.content



def read_text_file(file_path):
    """Reads a text file and returns its contents as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {e}"