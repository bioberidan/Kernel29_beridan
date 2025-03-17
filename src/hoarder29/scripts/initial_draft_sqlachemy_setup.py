from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CasesBench(Base):
    __tablename__ = 'cases_bench'
    id = Column(Integer, primary_key=True)
    hospital = Column(String(255))
    original_text = Column(Text)
    metadata = Column(JSON)
    processed_date = Column(DateTime)
    source_type = Column(String(50))
    source_file_path = Column(Text)

class CasesBenchMetadata(Base):
    __tablename__ = 'cases_bench_metadata'
    id = Column(Integer, primary_key=True)
    cases_bench_id = Column(Integer)
    __table_args__ = (ForeignKeyConstraint(['cases_bench_id'], ['cases_bench.id'], ondelete='CASCADE'),)










class CasesBenchGoldDiagnosis(Base):
    __tablename__ = 'cases_bench_gold_diagnosis'
    id = Column(Integer, primary_key=True)
    cases_bench_id = Column(Integer)
    __table_args__ = (ForeignKeyConstraint(['cases_bench_id'], ['cases_bench.id'], ondelete='CASCADE'),)

class LlmDiagnosis(Base):
    __tablename__ = 'llm_diagnosis'
    id = Column(Integer, primary_key=True)
    cases_bench_id = Column(Integer)
    model_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'))
    prompt_id = Column(Integer, ForeignKey('prompts.id', ondelete='CASCADE'))
    timestamp = Column(DateTime)
    __table_args__ = (ForeignKeyConstraint(['cases_bench_id'], ['cases_bench.id'], ondelete='CASCADE'),)

class LlmDiagnosisRank(Base):
    __tablename__ = 'llm_diagnosis_rank'
    id = Column(Integer, primary_key=True)
    cases_bench_id = Column(Integer)
    llm_diagnosis_id = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint(['cases_bench_id'], ['cases_bench.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['llm_diagnosis_id'], ['llm_diagnosis.id'], ondelete='CASCADE'),
    )

class LlmDiagnosisBySeverity(Base):
    __tablename__ = 'llm_diagnosis_by_severity'
    id = Column(Integer, primary_key=True)
    cases_bench_id = Column(Integer)
    llm_diagnosis_id = Column(Integer)
    severity_id = Column(Integer, ForeignKey('severity_levels.id', ondelete='CASCADE'))
    __table_args__ = (
        ForeignKeyConstraint(['cases_bench_id'], ['cases_bench.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['llm_diagnosis_id'], ['llm_diagnosis.id'], ondelete='CASCADE'),
    )

class LlmDiagnosisBySemanticRelationship(Base):
    __tablename__ = 'llm_diagnosis_by_semantic_relationship'
    id = Column(Integer, primary_key=True)
    cases_bench_id = Column(Integer)
    llm_diagnosis_id = Column(Integer)
    diagnosis_semantic_relationship_id = Column(Integer, ForeignKey('diagnosis_semantic_relationship.id', ondelete='CASCADE'))
    __table_args__ = (
        ForeignKeyConstraint(['cases_bench_id'], ['cases_bench.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['llm_diagnosis_id'], ['llm_diagnosis.id'], ondelete='CASCADE'),
    )

class SeverityLevels(Base):
    __tablename__ = 'severity_levels'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(Text)

class DiagnosisSemanticRelationship(Base):
    __tablename__ = 'diagnosis_semantic_relationship'
    id = Column(Integer, primary_key=True)
    semantic_relationship = Column(String(255))
    description = Column(Text)

class Models(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    alias = Column(String(255))
    name = Column(String(255))
    provider = Column(String(255))

class Prompts(Base):
    __tablename__ = 'prompts'
    id = Column(Integer, primary_key=True)
    alias = Column(String(255))
    description = Column(Text)
